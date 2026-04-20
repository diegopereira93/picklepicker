import os
import json
import logging
import re
import time
from typing import Optional

from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from pipeline.db.connection import get_connection
from pipeline.alerts.telegram import send_telegram_alert
from pipeline.utils.security import scrub_sensitive_data, SensitiveDataFilter
from pipeline.crawlers.utils import (
    normalize_paddle_name,
    validate_image_belongs_to_product,
    extract_brand_from_name,
)
from pipeline.dedup.normalizer import tier2_match, title_hash
from pipeline.dedup.spec_matcher import fuzzy_match_paddles

try:
    from pipeline.crawlers.validation import validate_product
except ImportError:
    validate_product = None

logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

DROPSHOT_BRASIL_URL = "https://www.dropshotbrasil.com.br/raquetes"

PRODUCT_KEYWORDS = ["Raquete", "Paddle", "Pickleball"]

FIRECRAWL_SCHEMA = {
    "type": "object",
    "properties": {
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price_brl": {"type": "number"},
                    "in_stock": {"type": "boolean"},
                    "image_url": {"type": "string"},
                    "product_url": {"type": "string"},
                    "brand": {"type": "string"},
                    "specs": {"type": "object"},
                },
            },
        }
    },
}

GRAMS_TO_OZ = 1 / 28.3495


def _get_markdown(result) -> str:
    if hasattr(result, "markdown"):
        return result.markdown
    elif isinstance(result, dict):
        return result.get("markdown", "")
    return str(result) if result else ""


def _try_structured_extraction(result) -> list[dict]:
    """Extract products from Firecrawl structured extraction result."""
    extract_data = None

    if hasattr(result, "extract") and result.extract:
        extract_data = result.extract
    elif isinstance(result, dict):
        extract_data = result.get("extract") or result.get("data")

    if not extract_data or not isinstance(extract_data, dict):
        return []

    raw_products = extract_data.get("products", [])
    if not raw_products:
        return []

    products = []
    for p in raw_products:
        if not isinstance(p, dict) or not p.get("name"):
            continue

        products.append({
            "name": str(p.get("name", "")),
            "price_brl": p.get("price_brl"),
            "in_stock": bool(p.get("in_stock", True)),
            "image_url": str(p.get("image_url", "")),
            "product_url": str(p.get("product_url", "")),
            "brand": extract_brand_from_name(str(p.get("name", ""))),
            "specs": p.get("specs") or {},
        })

    return products


def _parse_markdown_products(markdown: str) -> dict:
    lines = markdown.split("\n")
    products = []

    i = 0
    while i < len(lines):
        line = lines[i]

        has_keyword = any(kw in line for kw in PRODUCT_KEYWORDS)
        if not (has_keyword and len(line.strip()) > 20):
            i += 1
            continue

        price = None
        price_line_idx = -1
        for j in range(i + 1, min(i + 20, len(lines))):
            if "R$" in lines[j]:
                price_match = re.search(r"R\$([\d\.,]+)", lines[j])
                if price_match:
                    price_str = price_match.group(1)
                    price = float(price_str.replace(".", "").replace(",", "."))
                    price_line_idx = j
                    break

        if price is None:
            i += 1
            continue

        name = line.strip().lstrip("#").lstrip("*").lstrip("-").strip()

        product_url = ""
        for j in range(max(0, i - 10), i):
            prev_line = lines[j]
            if "dropshotbrasil.com.br" in prev_line and "](" in prev_line:
                url_match = re.search(r"\]\((https?://[^\)]+)", prev_line)
                if url_match:
                    product_url = url_match.group(1).rstrip('"').rstrip("'")
                    break

        products.append({
            "name": name,
            "price_brl": price,
            "product_url": product_url,
            "url": product_url,
            "image_url": "",
            "brand": extract_brand_from_name(name),
            "in_stock": True,
            "specs": {},
        })

        i = price_line_idx + 1 if price_line_idx > i else i + 1

    logger.info("Parsed %d products from markdown fallback", len(products))
    return {"data": {"products": products}}


def extract_specs_from_markdown(markdown: str) -> dict:
    """Extract paddle specifications from product page markdown.

    Parses PT-BR patterns:
    - Peso: Xg           → weight_oz (converted from grams)
    - Material do Face: … → face_material
    - Espessura: Xmm     → core_thickness_mm
    - Cabo: …             → grip_size
    - Núcleo: …          → core_material (kept in specs dict only, no DB column)

    Returns:
        dict with keys matching paddle_specs columns:
        weight_oz, face_material, core_thickness_mm, grip_size
    """
    specs: dict = {}

    weight_match = re.search(
        r"Peso[:\s]+(\d+(?:[.,]\d+)?)\s*g", markdown, re.IGNORECASE
    )
    if weight_match:
        weight_g = float(weight_match.group(1).replace(",", "."))
        specs["weight_oz"] = round(weight_g * GRAMS_TO_OZ, 2)

    face_match = re.search(
        r"(?:Material\s+do\s+Face|Face|Superf[ií]cie)[:\s]+([^\n,]+)",
        markdown,
        re.IGNORECASE,
    )
    if face_match:
        face_material = face_match.group(1).strip()
        if 2 < len(face_material) < 100:
            specs["face_material"] = face_material

    thickness_match = re.search(
        r"Espessura[:\s]+(\d+(?:[.,]\d+)?)\s*mm", markdown, re.IGNORECASE
    )
    if thickness_match:
        specs["core_thickness_mm"] = float(
            thickness_match.group(1).replace(",", ".")
        )

    grip_match = re.search(
        r"(?:Cabo|Grip|Tamanho\s+do\s+Cabo)[:\s]+([^\n,]+)",
        markdown,
        re.IGNORECASE,
    )
    if grip_match:
        grip_size = grip_match.group(1).strip()
        if 0 < len(grip_size) < 50:
            specs["grip_size"] = grip_size

    core_match = re.search(r"N[uú]cleo[:\s]+([^\n,]+)", markdown, re.IGNORECASE)
    if core_match:
        core_material = core_match.group(1).strip()
        if 2 < len(core_material) < 100:
            specs["core_material"] = core_material

    return specs


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=10, max=120),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def extract_products(app: FirecrawlApp, url: str) -> dict:
    try:
        result = app.scrape(
            url,
            params={
                "formats": ["extract", "markdown"],
                "extract": {"schema": FIRECRAWL_SCHEMA},
            },
        )
    except TypeError:
        logger.debug("Structured extraction params not supported, using basic scrape")
        result = app.scrape(url)

    products = _try_structured_extraction(result)
    if products:
        logger.info("Extracted %d products via structured extraction", len(products))
        return {"data": {"products": products}}

    markdown = _get_markdown(result)
    return _parse_markdown_products(markdown)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def scrape_product_page(app: FirecrawlApp, url: str) -> Optional[str]:
    try:
        result = app.scrape(url)
        if hasattr(result, "markdown"):
            markdown = result.markdown
        elif isinstance(result, dict):
            markdown = result.get("markdown", "")
        else:
            return None
        return extract_image_from_markdown(markdown)
    except Exception as e:
        logger.warning("Failed to scrape product page %s: %s", url, e)
        return None


def extract_image_from_markdown(markdown: str) -> Optional[str]:
    pattern = r"!\[.*?\]\((https?://[^)]+\.(?:jpg|jpeg|png|webp))\)"
    matches = re.findall(pattern, markdown, re.IGNORECASE)

    cdn_patterns = [
        "dropshot.com.br",
        "dropshotbrasil.com.br",
        "cloudfront.net",
        "amazonaws.com",
        "cdn",
    ]

    for match in matches:
        if any(cdn in match.lower() for cdn in cdn_patterns):
            return match

    if matches and len(matches[0]) > 80:
        return matches[0]

    return None


async def save_products_to_db(products: list[dict], retailer_id: int, conn) -> int:
    """Save extracted products to paddles + price_snapshots + paddle_specs.

    Uses atomic upsert for paddles (INSERT ... ON CONFLICT DO UPDATE)
    to avoid TOCTOU race conditions. Requires UNIQUE constraint on
    paddles.name.

    Validates each product before saving. Skips invalid ones and logs reasons.
    Returns count of saved snapshots.
    """
    saved = 0
    for product in products:
        price = product.get("price_brl")
        if price is None:
            logger.warning(
                "Skipping product %s: missing price_brl",
                product.get("name", "unknown"),
            )
            continue

        if validate_product is not None:
            is_valid, reasons = validate_product(product)
            if not is_valid:
                logger.warning(
                    "Skipping invalid product %s: %s",
                    product.get("name", "unknown"),
                    "; ".join(reasons),
                )
                continue
        else:
            name = product.get("name", "")
            if not name or len(name.strip()) < 3:
                logger.warning("Skipping product with invalid name: %r", name)
                continue

        raw_name = product.get("name", "")
        name = normalize_paddle_name(raw_name)
        brand = product.get("brand", "") or extract_brand_from_name(raw_name)
        image_url = product.get("image_url", "")

        existing_id = await tier2_match(raw_name)
        if existing_id is not None:
            paddle_id = existing_id
            logger.info(
                "Dedup tier-2 match for '%s': reusing paddle_id=%d",
                name, paddle_id,
            )
        else:
            fuzzy_id, fuzzy_score = await fuzzy_match_paddles(raw_name, threshold=0.85)

            hash_value = title_hash(raw_name)
            result = await conn.execute(
                """
                INSERT INTO paddles (name, brand, model, image_url, in_stock, price_min_brl, title_hash)
                VALUES (%(name)s, %(brand)s, %(model)s, %(image_url)s, %(in_stock)s, %(price_min_brl)s, %(title_hash)s)
                ON CONFLICT (name) DO UPDATE SET
                    brand = EXCLUDED.brand,
                    model = EXCLUDED.model,
                    image_url = COALESCE(NULLIF(EXCLUDED.image_url, ''), paddles.image_url),
                    in_stock = EXCLUDED.in_stock,
                    price_min_brl = LEAST(paddles.price_min_brl, EXCLUDED.price_min_brl),
                    title_hash = EXCLUDED.title_hash,
                    updated_at = NOW()
                RETURNING id
                """,
                {
                    "name": name,
                    "brand": brand or "",
                    "model": name,
                    "image_url": image_url,
                    "in_stock": product.get("in_stock", True),
                    "price_min_brl": price,
                    "title_hash": hash_value,
                },
            )
            row = await result.fetchone()
            if row is None:
                logger.error("Upsert failed for paddle: %s", name)
                continue

            paddle_id = row[0]

            # Log potential duplicate to review_queue (conservative: still saved)
            if fuzzy_id is not None:
                logger.warning(
                    "Dedup fuzzy match for '%s': similar to paddle_id=%d (score=%.3f) — logged to review_queue",
                    name, fuzzy_id, fuzzy_score,
                )
                await conn.execute(
                    """
                    INSERT INTO review_queue (type, paddle_id, related_paddle_id, data, status)
                    VALUES ('duplicate', %(paddle_id)s, %(related_id)s, %(data)s, 'pending')
                    """,
                    {
                        "paddle_id": fuzzy_id,
                        "related_id": paddle_id,
                        "data": json.dumps({"raw_name": raw_name, "score": fuzzy_score}),
                    },
                )

            specs = product.get("specs") or {}
            spec_fields: dict = {}
            if specs.get("weight_oz") is not None:
                spec_fields["weight_oz"] = specs["weight_oz"]
            if specs.get("face_material"):
                spec_fields["face_material"] = specs["face_material"]
            if specs.get("core_thickness_mm") is not None:
                spec_fields["core_thickness_mm"] = specs["core_thickness_mm"]
            if specs.get("grip_size"):
                spec_fields["grip_size"] = specs["grip_size"]

            if spec_fields:
                columns = list(spec_fields.keys())
                placeholders = ", ".join(f"%({c})s" for c in columns)
                set_clauses = ", ".join(
                    f"{col} = EXCLUDED.{col}" for col in columns
                )

                await conn.execute(
                    f"""
                    INSERT INTO paddle_specs (paddle_id, {', '.join(columns)})
                    VALUES (%(paddle_id)s, {placeholders})
                    ON CONFLICT (paddle_id) DO UPDATE SET
                        {set_clauses}, updated_at = NOW()
                    """,
                    {"paddle_id": paddle_id, **spec_fields},
                )

        # Always record price snapshot (for both tier-2 matches and new paddles)
        await conn.execute(
            """
            INSERT INTO price_snapshots
                (paddle_id, retailer_id, price_brl, currency, in_stock, affiliate_url, scraped_at, source_raw)
            VALUES
                (%(paddle_id)s, %(retailer_id)s, %(price_brl)s, 'BRL', %(in_stock)s, %(affiliate_url)s, NOW(), %(source_raw)s)
            """,
            {
                "paddle_id": paddle_id,
                "retailer_id": retailer_id,
                "price_brl": price,
                "in_stock": product.get("in_stock", True),
                "affiliate_url": product.get("product_url", ""),
                "source_raw": json.dumps(product),
            },
        )
        saved += 1

    return saved


async def run_dropshot_brasil_crawler(app: FirecrawlApp | None = None) -> int:
    """Main entry point: extract from Drop Shot Brasil, save to DB.

    Returns count of saved rows. Raises after sending Telegram alert if all
    3 Firecrawl retries are exhausted.
    """
    if app is None:
        app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])

    try:
        result = extract_products(app, DROPSHOT_BRASIL_URL)
    except Exception as e:
        safe_message = scrub_sensitive_data(str(e))
        logger.error("Drop Shot Brasil crawler failed: %s", safe_message)
        await send_telegram_alert(
            f"Drop Shot Brasil crawler failed after 3 retries: {safe_message}"
        )
        raise type(e)(safe_message) from e

    if hasattr(result, "model_dump"):
        result = result.model_dump()
    elif hasattr(result, "dict"):
        result = result.dict()

    products = (result.get("data") or {}).get("products", [])
    logger.info("Extracted %d products from Drop Shot Brasil", len(products))

    logger.info(
        "Starting Phase 2: Scraping individual product pages for images and specs..."
    )
    for i, product in enumerate(products):
        product_url = product.get("product_url") or product.get("url")
        current_image = product.get("image_url", "")
        product_name = product.get("name", "")

        if product_url:
            logger.debug(
                "Scraping product page %d/%d: %s",
                i + 1,
                len(products),
                product_url,
            )
            try:
                page_result = app.scrape(product_url)
                page_markdown = _get_markdown(page_result)

                phase2_image = (
                    extract_image_from_markdown(page_markdown)
                    if page_markdown
                    else None
                )

                if phase2_image:
                    should_replace = False

                    if not current_image:
                        should_replace = True
                    elif "placeholder" in current_image.lower():
                        should_replace = True
                    elif len(phase2_image) > len(current_image) + 20:
                        should_replace = True

                    if should_replace and not validate_image_belongs_to_product(
                        phase2_image, product_name
                    ):
                        logger.warning(
                            "Phase 2 image for '%s' may not belong to product",
                            product_name[:40],
                        )
                        if not current_image or "placeholder" in current_image.lower():
                            pass
                        else:
                            should_replace = False

                    if should_replace:
                        product["image_url"] = phase2_image
                        logger.info(
                            "Phase 2 image for '%s...': %s...",
                            product_name[:40],
                            phase2_image[:60],
                        )

                if page_markdown:
                    page_specs = extract_specs_from_markdown(page_markdown)
                    if page_specs:
                        existing_specs = product.get("specs") or {}
                        existing_specs.update(page_specs)
                        product["specs"] = existing_specs
                        logger.info(
                            "Phase 2 specs for '%s': %s",
                            product_name[:40],
                            list(page_specs.keys()),
                        )
            except Exception as e:
                logger.warning(
                    "Failed to scrape product page %s: %s", product_url, e
                )

        if i < len(products) - 1:
            time.sleep(1)

    products_with_images = [p for p in products if p.get("image_url")]
    products_with_specs = [p for p in products if p.get("specs")]
    logger.info(
        "Phase 2 complete: %d/%d images, %d/%d specs",
        len(products_with_images),
        len(products),
        len(products_with_specs),
        len(products),
    )

    if not products:
        logger.warning("No products extracted from Drop Shot Brasil")
        return 0

    async with get_connection() as conn:
        # Note: get_connection() context manager automatically rolls back
        # on exception to prevent pool poisoning. Connection returned clean.
        saved = await save_products_to_db(products, retailer_id=3, conn=conn)
        await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices")
        await conn.commit()

    logger.info("Saved %d products to price_snapshots", saved)
    return saved


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_dropshot_brasil_crawler())
