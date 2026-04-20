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
from pipeline.crawlers.utils import extract_brand_from_name, normalize_paddle_name, validate_image_belongs_to_product
from pipeline.crawlers.validation import validate_product
from pipeline.dedup.normalizer import tier2_match, title_hash
from pipeline.dedup.spec_matcher import fuzzy_match_paddles

logger = logging.getLogger(__name__)

BRAZIL_STORE_URL = "https://www.brazilpickleballstore.com.br/raquete/"

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
                    "specs": {
                        "type": "object",
                        "properties": {
                            "weight_oz": {"type": "number"},
                            "face_material": {"type": "string"},
                            "core_material": {"type": "string"},
                            "core_thickness_mm": {"type": "number"},
                            "grip_size": {"type": "string"},
                        },
                    },
                },
            },
        }
    },
}

GRAMS_TO_OZ = 1 / 28.3495

FACE_MATERIAL_MAP = {
    "carbono": "Carbon Fiber",
    "carbon": "Carbon Fiber",
    "fibra de carbono": "Carbon Fiber",
    "carbon fiber": "Carbon Fiber",
    "fibra de vidro": "Fiberglass",
    "fiberglass": "Fiberglass",
    "glass fiber": "Fiberglass",
    "grafite": "Graphite",
    "graphite": "Graphite",
    "kevlar": "Kevlar",
    "hybrid": "Hybrid",
    "t700": "T700 Carbon Fiber",
}


def extract_specs_from_markdown(markdown: str) -> dict:
    """Parse PT-BR spec patterns from product page markdown.

    Recognizes patterns like:
      Peso: 230g / 8.1 oz
      Face: Carbono / Fiberglass / Graphite
      Núcleo: PP / Polymer / Polipropileno
      Espessura: 16mm
      Cabo / Grip: 4.25"
    """
    specs: dict = {}
    text = markdown.lower()

    # Weight: "Peso: 230g" or "230 g" or "8.1 oz" or "8.1oz"
    weight_match = re.search(r"peso[:\s]+(\d+(?:[.,]\d+)?)\s*g", text)
    if weight_match:
        grams = float(weight_match.group(1).replace(",", "."))
        specs["weight_oz"] = round(grams * GRAMS_TO_OZ, 2)
    else:
        oz_match = re.search(r"(\d+(?:[.,]\d+)?)\s*oz", text)
        if oz_match:
            specs["weight_oz"] = float(oz_match.group(1).replace(",", "."))

    # Face material: "Face: Carbono" or "Superfície: Fiberglass" or "Material da Face: ..."
    face_match = re.search(
        r"(?:face|superf[ií]cie|material\s+da\s+face)[:\s]+([a-zà-úa-z\s]+?)(?:\n|,|\.|$)",
        text,
    )
    if face_match:
        raw_face = face_match.group(1).strip()
        for pt_key, en_val in FACE_MATERIAL_MAP.items():
            if pt_key in raw_face:
                specs["face_material"] = en_val
                break

    # Core thickness: "Espessura: 16mm" or "16 mm"
    thickness_match = re.search(r"espessura[:\s]+(\d+(?:[.,]\d+)?)\s*mm", text)
    if thickness_match:
        specs["core_thickness_mm"] = float(thickness_match.group(1).replace(",", "."))

    # Grip size: "Cabo: 4.25\"" or "Grip: 4 1/4" or "Punho: ..."
    grip_match = re.search(r"(?:cabo|grip|punho)[:\s]+([\d\s/]+(?:\"|'))", text)
    if grip_match:
        specs["grip_size"] = grip_match.group(1).strip().rstrip("\"'").strip()

    return specs


def _try_structured_extraction(app: FirecrawlApp, url: str) -> list[dict]:
    """Attempt Firecrawl structured extraction (JSON format with schema).

    Returns list of product dicts, or empty list on failure.
    """
    try:
        result = app.scrape(
            url,
            formats=[{
                "type": "json",
                "prompt": (
                    "Extract all pickleball paddle products from this page. "
                    "For each product include: name, price_brl (as number), "
                    "in_stock (boolean), image_url, product_url, brand, and specs "
                    "(weight_oz, face_material, core_material, core_thickness_mm, grip_size)."
                ),
                "schema": FIRECRAWL_SCHEMA,
            }],
        )
        products = []
        if hasattr(result, "json") and result.json:
            data = result.json
        elif hasattr(result, "extract") and result.extract:
            data = result.extract
        elif isinstance(result, dict):
            data = result.get("json") or result.get("extract") or {}
        else:
            return []

        extracted = data.get("products", []) if isinstance(data, dict) else []
        for item in extracted:
            if not isinstance(item, dict) or not item.get("name"):
                continue
            product = {
                "name": item.get("name", ""),
                "price_brl": item.get("price_brl"),
                "in_stock": item.get("in_stock", True),
                "image_url": item.get("image_url", ""),
                "product_url": item.get("product_url", ""),
                "url": item.get("product_url", ""),
                "brand": item.get("brand", ""),
                "specs": item.get("specs", {}),
            }
            if product["price_brl"] is not None:
                try:
                    product["price_brl"] = float(product["price_brl"])
                except (ValueError, TypeError):
                    product["price_brl"] = None
            products.append(product)

        logger.info("Structured extraction returned %d products", len(products))
        return products
    except Exception as e:
        logger.warning("Structured extraction failed, will use markdown fallback: %s", e)
        return []


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=10, max=120),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def extract_products(app: FirecrawlApp, url: str) -> dict:
    """Extract paddle products: try structured extraction first, fallback to markdown."""
    # Phase 1: Try structured extraction
    structured = _try_structured_extraction(app, url)
    if len(structured) >= 3:
        return {"data": {"products": structured}}

    logger.info(
        "Structured extraction returned %d products (< 3 threshold), using markdown parsing",
        len(structured),
    )

    # Phase 2: Fallback — markdown parsing (original logic preserved)
    result = app.scrape(url)

    if hasattr(result, 'markdown'):
        markdown = result.markdown
    elif isinstance(result, dict):
        markdown = result.get('markdown', '')
    else:
        markdown = str(result)

    lines = markdown.split('\n')
    products = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith('[Raquete'):
            name = line[9:].rstrip('\\').strip()
            full_name = 'Raquete ' + name

            price = None
            for j in range(i+1, min(i+20, len(lines))):
                if lines[j].startswith('R$') and '\\\\n\\\\n' not in lines[j]:
                    price_match = re.search(r'R\$([\d\.,]+)', lines[j])
                    if price_match:
                        price_str = price_match.group(1)
                        price = float(price_str.replace('.', '').replace(',', '.'))
                        break

            product_url = ''
            for j in range(max(0, i-10), i):
                prev_line = lines[j]
                if 'brazilpickleballstore.com.br/produtos/' in prev_line:
                    url_match = re.search(r'\]\((https?://[^\)]+)\s*"', prev_line)
                    if url_match:
                        product_url = url_match.group(1).rstrip('"')
                        break
                    url_match2 = re.search(r'https?://[^\s\)]+produtos[^\s\)]+', prev_line)
                    if url_match2:
                        product_url = url_match2.group(0)
                        break

            if price:
                products.append({
                    "name": full_name,
                    "price_brl": price,
                    "product_url": product_url,
                    "url": product_url,
                    "image_url": "",
                    "brand": extract_brand_from_name(full_name),
                    "in_stock": True,
                    "specs": {},
                })

        i += 1

    logger.info("Parsed %d products from markdown", len(products))

    return {"data": {"products": products}}


def extract_image_from_markdown(markdown: str) -> Optional[str]:
    """Extract image URL from markdown content using regex.

    Handles multiple CDN patterns with priority ordering:
    1. mitiendanube.com (Brazil Store's CDN) - with size transformation
    2. cloudfront.net
    3. amazonaws.com
    4. any URL containing 'cdn'
    5. fallback: first match if URL length > 80 chars
    """
    pattern = r'!\[.*?\]\((https?://[^)]+\.(?:jpg|jpeg|png|webp))\)'
    matches = re.findall(pattern, markdown, re.IGNORECASE)
    
    if not matches:
        return None
    
    # Priority 1: mitiendanube.com (Brazil Store's CDN)
    for match in matches:
        if 'mitiendanube.com' in match:
            return match.replace('-1024-1024', '-480-0')
    
    # Priority 2: cloudfront.net
    for match in matches:
        if 'cloudfront.net' in match:
            return match
    
    # Priority 3: amazonaws.com
    for match in matches:
        if 'amazonaws.com' in match:
            return match
    
    # Priority 4: any URL containing 'cdn'
    for match in matches:
        if 'cdn' in match:
            return match
    
    # Fallback: first match if URL length > 80 chars (likely a specific product image)
    for match in matches:
        if len(match) > 80:
            return match
    
    # Last resort: return first match
    return matches[0] if matches else None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def scrape_product_page(app: FirecrawlApp, product_url: str) -> Optional[tuple[str, dict]]:
    """Scrape individual product page for image URL and specs.

    Returns (image_url, specs_dict) or None on failure.
    """
    try:
        result = app.scrape(product_url)
        if hasattr(result, 'markdown'):
            markdown = result.markdown
        elif isinstance(result, dict):
            markdown = result.get('markdown', '')
        else:
            return None

        image_url = extract_image_from_markdown(markdown)
        specs = extract_specs_from_markdown(markdown)
        return (image_url, specs)
    except Exception as e:
        logger.warning("Failed to scrape product page %s: %s", product_url, e)
        return None


async def save_products_to_db(products: list[dict], retailer_id: int, conn) -> int:
    """Save extracted products to paddles + price_snapshots + paddle_specs.

    Uses atomic upsert for paddles (INSERT ... ON CONFLICT DO UPDATE)
    to avoid TOCTOU race conditions. Requires UNIQUE constraint on
    paddles.name.

    Validates products before insertion. Skips invalid with warning log.
    Also upserts paddle_specs when specs are present.
    """
    saved = 0
    for product in products:
        is_valid, errors = validate_product(product)
        if not is_valid:
            logger.warning(
                "Skipping invalid product %s: %s",
                product.get("name", "unknown"),
                "; ".join(errors),
            )
            continue

        price = product.get("price_brl")
        if price is None:
            logger.warning(
                "Skipping product %s: missing price_brl", product.get("name", "unknown")
            )
            continue

        raw_name = product.get("name", "")
        name = normalize_paddle_name(raw_name)
        raw_brand = product.get("brand", "")
        brand = raw_brand if raw_brand else extract_brand_from_name(raw_name)
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

            # Upsert paddle_specs if any specs present
            specs = product.get("specs", {})
            if specs and any(specs.values()):
                spec_cols = []
                spec_params: dict = {"paddle_id": paddle_id}
                if specs.get("weight_oz") is not None:
                    spec_cols.append("weight_oz")
                    spec_params["weight_oz"] = specs["weight_oz"]
                if specs.get("face_material"):
                    spec_cols.append("face_material")
                    spec_params["face_material"] = specs["face_material"]
                if specs.get("core_thickness_mm") is not None:
                    spec_cols.append("core_thickness_mm")
                    spec_params["core_thickness_mm"] = specs["core_thickness_mm"]
                if specs.get("grip_size"):
                    spec_cols.append("grip_size")
                    spec_params["grip_size"] = specs["grip_size"]

                if spec_cols:
                    set_clause = ", ".join(f"{col} = EXCLUDED.{col}" for col in spec_cols)
                    col_names = ", ".join(["paddle_id"] + spec_cols)
                    placeholders = ", ".join(f"%({col})s" for col in ["paddle_id"] + spec_cols)
                    await conn.execute(
                        f"""
                        INSERT INTO paddle_specs ({col_names})
                        VALUES ({placeholders})
                        ON CONFLICT (paddle_id) DO UPDATE SET {set_clause}, updated_at = NOW()
                        """,
                        spec_params,
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


async def run_brazil_store_crawler(app: FirecrawlApp | None = None) -> int:
    """Main entry point: extract from Brazil Pickleball Store, save to DB.

    Returns count of saved rows. Raises after sending Telegram alert if all
    3 Firecrawl retries are exhausted.
    """
    if app is None:
        app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])

    try:
        result = extract_products(app, BRAZIL_STORE_URL)
    except Exception as e:
        await send_telegram_alert(
            f"Brazil Pickleball Store crawler failed after 3 retries: {e}"
        )
        raise

    # Convert ExtractResponse to dict if needed
    if hasattr(result, 'model_dump'):
        result = result.model_dump()
    elif hasattr(result, 'dict'):
        result = result.dict()

    products = (result.get("data") or {}).get("products", [])
    logger.info("Extracted %d products from Brazil Pickleball Store", len(products))

    # Phase 2: Scrape individual product pages for images + specs
    logger.info("Starting Phase 2: Scraping individual product pages for images and specs...")
    for i, product in enumerate(products):
        product_url = product.get("product_url") or product.get("url")
        current_image = product.get("image_url", "")
        product_name = product.get("name", "Unknown")

        # Always scrape if product_url exists - improved confidence-based replacement
        if product_url:
            logger.debug(f"Scraping product page {i+1}/{len(products)}: {product_url}")
            phase2_result = scrape_product_page(app, product_url)
            if phase2_result:
                phase2_image, phase2_specs = phase2_result

                # Merge specs: Phase 2 product-page specs override list-page specs
                if phase2_specs and any(phase2_specs.values()):
                    existing_specs = product.get("specs", {})
                    merged = {**existing_specs, **{k: v for k, v in phase2_specs.items() if v}}
                    product["specs"] = merged

                # Image replacement logic
                if phase2_image:
                    should_replace = False
                    if not current_image:
                        should_replace = True
                    elif "placeholder" in current_image.lower():
                        should_replace = True
                    elif len(phase2_image) > len(current_image) + 20:
                        should_replace = True
                    elif current_image.count("/") < phase2_image.count("/"):
                        should_replace = True
                    
                    if should_replace and not validate_image_belongs_to_product(phase2_image, product_name):
                        logger.warning(f"Phase 2 image for '{product_name[:40]}' may not belong to product: {phase2_image[:60]}...")
                        if not current_image or "placeholder" in current_image.lower():
                            pass
                        else:
                            should_replace = False

                    if should_replace:
                        product["image_url"] = phase2_image
                        logger.info(f"Phase 2 image for '{product_name[:40]}...': {phase2_image[:60]}...")
            
            # Rate limiting: sleep between scrapes
            if i < len(products) - 1:
                time.sleep(1)

    # Count products with images
    products_with_images = [p for p in products if p.get("image_url")]
    products_with_specs = [p for p in products if p.get("specs") and any(p["specs"].values())]
    logger.info(
        f"Phase 2 complete: {len(products_with_images)}/{len(products)} images, "
        f"{len(products_with_specs)}/{len(products)} with specs"
    )

    if not products:
        logger.warning("No products extracted from Brazil Pickleball Store")
        return 0

    async with get_connection() as conn:
        # retailer_id=1 is Brazil Pickleball Store (from seed data in schema.sql)
        saved = await save_products_to_db(products, retailer_id=1, conn=conn)
        await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices")
        await conn.commit()

    logger.info("Saved %d products to price_snapshots", saved)
    return saved


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_brazil_store_crawler())
