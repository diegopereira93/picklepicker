"""JOOLA Brazil Shopify JSON API crawler.

Scrapes pickleball paddles from https://www.joola.com.br using Shopify's
native JSON endpoints (no Firecrawl required). Extracts product details,
prices, images, and specifications from HTML descriptions.

retailer_id = 2 (JOOLA, replacing former Mercado Livre slot).
"""

import asyncio
import json
import logging
import re
from html.parser import HTMLParser
from typing import Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from pipeline.alerts.telegram import send_telegram_alert
from pipeline.crawlers.utils import normalize_paddle_name, extract_brand_from_name
from pipeline.db.connection import get_connection
from pipeline.dedup.normalizer import tier2_match, title_hash
from pipeline.dedup.spec_matcher import fuzzy_match_paddles

logger = logging.getLogger(__name__)

JOOLA_BASE_URL = "https://www.joola.com.br"
COLLECTION_PATH = "/collections/pickleball"
PRODUCTS_JSON_URL = f"{JOOLA_BASE_URL}{COLLECTION_PATH}/products.json"
PRODUCT_DETAIL_URL = f"{JOOLA_BASE_URL}/products"

# Shopify paginates max 250 products per page
PAGE_SIZE = 250

# Keywords that indicate non-paddle products to filter out
EXCLUDE_KEYWORDS = {
    "bola", "ball", "bolinhas", "bag", "mochila", "bolso", "luva",
    "sapato", "shoe", "tenis", "camisa", "shirt", "bermuda", "short",
    "meia", "sock", "headband", "faixa", "boné", "cap", "acessorio",
    "accessory", "grip", "overgrip", "eyewear", "oculos", "hat",
    "visor", "protetor", "case", "capa", "conjunto", "kit",
    "backpack", "rack", "cart", "torre", "net", "rede", "post",
}

# Keywords that confirm a product IS a paddle
PADDLE_KEYWORDS = {
    "paddle", "raquete", "raquet", "paddles", "raquetes",
}


class HTMLTextExtractor(HTMLParser):
    """Strip HTML tags and return plain text."""

    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []

    def handle_data(self, data: str) -> None:
        self._pieces.append(data)

    def get_text(self) -> str:
        return " ".join(self._pieces)


def _strip_html(html: str) -> str:
    """Remove HTML tags from a string, returning plain text."""
    extractor = HTMLTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


def extract_specs_from_html(html_content: str) -> dict:
    """Parse product description HTML for paddle specifications.

    Looks for PT-BR and EN patterns for weight, face material, core
    material, thickness, and grip size.

    Returns a dict with keys matching paddle_specs columns:
        weight_oz, face_material, core_thickness_mm, grip_size
    """
    if not html_content:
        return {}

    text = _strip_html(html_content)
    # Normalize whitespace for easier regex matching
    text = re.sub(r"\s+", " ", text).strip()

    specs: dict = {}

    # --- Weight ---
    # PT-BR: "Peso: 230g" / "Peso: 8.1 oz"
    weight_match = re.search(
        r"Peso\s*[:\-]?\s*([\d,.]+)\s*(g|gramas|oz|ounces)", text, re.IGNORECASE
    )
    if not weight_match:
        # EN: "Weight: 8.1 oz" / "Weight: 230g"
        weight_match = re.search(
            r"Weight\s*[:\-]?\s*([\d,.]+)\s*(g|grams|oz|ounces)", text, re.IGNORECASE
        )
    if weight_match:
        value = float(weight_match.group(1).replace(",", "."))
        unit = weight_match.group(2).lower()
        if unit in ("g", "gramas", "grams"):
            specs["weight_oz"] = round(value / 28.3495, 2)
        else:
            specs["weight_oz"] = round(value, 2)

    # --- Face Material ---
    face_match = re.search(
        r"(?:Face|Superficie|Surface)\s*[:\-]?\s*([^\n,;]+?)(?:\n|,|;|$)",
        text, re.IGNORECASE
    )
    if face_match:
        face_val = face_match.group(1).strip()
        if len(face_val) < 80:
            specs["face_material"] = face_val

    # --- Core Thickness ---
    thickness_match = re.search(
        r"(?:Espessura|Thickness)\s*[:\-]?\s*([\d,.]+)\s*(mm)", text, re.IGNORECASE
    )
    if thickness_match:
        specs["core_thickness_mm"] = float(thickness_match.group(1).replace(",", "."))

    # --- Grip Size ---
    grip_match = re.search(
        r"(?:Cabo|Grip(?:\s+Size)?)\s*[:\-]?\s*([\d,.]+)\s*(cm|in|polegadas|inches|mm)",
        text, re.IGNORECASE
    )
    if grip_match:
        specs["grip_size"] = grip_match.group(0).strip()

    return specs


def is_paddle_product(title: str, product_type: str = "") -> bool:
    """Return True if the product is a pickleball paddle, not an accessory."""
    combined = f"{title} {product_type}".lower()

    # Explicitly exclude non-paddle items
    for kw in EXCLUDE_KEYWORDS:
        if kw in combined:
            return False

    # Must contain a paddle keyword
    for kw in PADDLE_KEYWORDS:
        if kw in combined:
            return True

    # If no paddle keyword found, assume it's not a paddle
    return False


def map_shopify_product(product: dict) -> Optional[dict]:
    """Convert a Shopify product JSON object to our internal format.

    Returns None if the product should be skipped (not a paddle).
    """
    title = product.get("title", "")
    product_type = product.get("product_type", "")
    handle = product.get("handle", "")

    if not is_paddle_product(title, product_type):
        logger.debug("Skipping non-paddle product: %s", title)
        return None

    # Price — use the first variant
    variants = product.get("variants", [])
    if not variants:
        logger.warning("No variants for product %s, skipping", title)
        return None

    first_variant = variants[0]
    price_str = first_variant.get("price", "0")
    try:
        price_brl = float(price_str)
    except (ValueError, TypeError):
        logger.warning("Invalid price '%s' for %s, skipping", price_str, title)
        return None

    if price_brl <= 0:
        logger.debug("Zero/negative price for %s, skipping", title)
        return None

    in_stock = first_variant.get("available", False)

    # Image — prefer highest quality (largest)
    images = product.get("images", [])
    image_url = ""
    if images:
        # Shopify images: pick the one with largest width or first available
        best_img = max(images, key=lambda img: img.get("width", 0))
        image_url = best_img.get("src", "")

    # Build product URL
    product_url = f"{JOOLA_BASE_URL}/products/{handle}"

    # Brand — JOOLA for all products unless vendor says otherwise
    vendor = product.get("vendor", "")
    brand = "JOOLA"
    if vendor and vendor.upper() != "JOOLA":
        brand = vendor

    # Parse specs from HTML body
    body_html = product.get("body_html", "")
    specs = extract_specs_from_html(body_html)

    return {
        "name": title,
        "brand": brand,
        "price_brl": price_brl,
        "in_stock": in_stock,
        "image_url": image_url,
        "product_url": product_url,
        "specs": specs,
    }


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
async def fetch_products_page(client: httpx.AsyncClient, page: int) -> list[dict]:
    """Fetch a single page of Shopify products.json.

    Returns the raw list of product dicts from Shopify.
    """
    response = await client.get(
        PRODUCTS_JSON_URL,
        params={"limit": PAGE_SIZE, "page": page},
    )
    response.raise_for_status()
    data = response.json()
    return data.get("products", [])


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectError, httpx.TimeoutException)),
    reraise=True,
)
async def fetch_product_detail(client: httpx.AsyncClient, handle: str) -> Optional[dict]:
    """Fetch detailed product data from Shopify product.json endpoint."""
    response = await client.get(f"{PRODUCT_DETAIL_URL}/{handle}.json")
    response.raise_for_status()
    data = response.json()
    return data.get("product")


async def fetch_all_products(client: httpx.AsyncClient) -> list[dict]:
    """Paginate through all Shopify products in the pickleball collection."""
    all_products: list[dict] = []
    page = 1

    while True:
        logger.info("Fetching JOOLA products page %d", page)
        products = await fetch_products_page(client, page)

        if not products:
            logger.info("Page %d returned 0 products — done paginating", page)
            break

        all_products.extend(products)
        logger.info("Page %d: %d products (total: %d)", page, len(products), len(all_products))

        # Shopify returns up to `limit` items per page.
        # If we got fewer than PAGE_SIZE, we've reached the end.
        if len(products) < PAGE_SIZE:
            break

        page += 1

    return all_products


async def save_products_to_db(products: list[dict], retailer_id: int, conn) -> int:
    """Save extracted products to paddles + price_snapshots + paddle_specs.

    Uses atomic upsert for paddles (INSERT ... ON CONFLICT DO UPDATE)
    to avoid TOCTOU race conditions. Requires UNIQUE constraint on
    paddles.name.

    Skips items without price_brl. Returns count of saved snapshots.
    """
    saved = 0
    for product in products:
        price = product.get("price_brl")
        if price is None:
            logger.warning(
                "Skipping product %s: missing price_brl", product.get("name", "unknown")
            )
            continue

        raw_name = product.get("name", "")
        name = normalize_paddle_name(raw_name)
        brand = product.get("brand", "")
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
            if specs:
                spec_cols = []
                spec_vals = {}
                for col, key in [
                    ("weight_oz", "weight_oz"),
                    ("face_material", "face_material"),
                    ("core_thickness_mm", "core_thickness_mm"),
                    ("grip_size", "grip_size"),
                ]:
                    if key in specs and specs[key] is not None:
                        spec_cols.append(col)
                        spec_vals[key] = specs[key]

                if spec_cols:
                    cols_sql = ", ".join(["paddle_id"] + spec_cols)
                    placeholders = ", ".join(["%(paddle_id)s"] + [f"%({c})s" for c in spec_cols])
                    update_sets = ", ".join(f"{c} = EXCLUDED.{c}" for c in spec_cols)

                    await conn.execute(
                        f"""
                        INSERT INTO paddle_specs (paddle_id, {', '.join(spec_cols)})
                        VALUES (%(paddle_id)s, {', '.join(f'%({c})s' for c in spec_cols)})
                        ON CONFLICT (paddle_id) DO UPDATE SET
                            {update_sets},
                            updated_at = NOW()
                        """,
                        {"paddle_id": paddle_id, **spec_vals},
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


async def run_joola_crawler() -> int:
    """Main entry point: extract JOOLA products via Shopify JSON API, save to DB.

    Returns count of saved rows. Raises after sending Telegram alert if all
    retries are exhausted.
    """
    all_mapped: list[dict] = []

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=10.0),
        headers={"Accept": "application/json"},
        follow_redirects=True,
    ) as client:
        try:
            raw_products = await fetch_all_products(client)
        except Exception as e:
            error_msg = str(e)
            logger.error("JOOLA crawler failed during fetch: %s", error_msg)
            await send_telegram_alert(f"JOOLA crawler failed: {error_msg}")
            raise

        logger.info("Fetched %d raw products from JOOLA Shopify", len(raw_products))

        # Map and filter products
        for raw in raw_products:
            mapped = map_shopify_product(raw)
            if mapped is not None:
                all_mapped.append(mapped)

        logger.info("Mapped %d paddle products (filtered from %d raw)", len(all_mapped), len(raw_products))

        # Fetch detailed specs for each product (rate-limited)
        if all_mapped:
            logger.info("Fetching detailed specs for %d products...", len(all_mapped))
            for i, product in enumerate(all_mapped):
                handle = product["product_url"].split("/")[-1]
                try:
                    detail = await fetch_product_detail(client, handle)
                    if detail:
                        body_html = detail.get("body_html", "")
                        if body_html:
                            new_specs = extract_specs_from_html(body_html)
                            if new_specs:
                                # Merge: detailed specs override listing specs
                                product["specs"] = {**(product.get("specs") or {}), **new_specs}
                except Exception as e:
                    logger.warning("Failed to fetch detail for %s: %s", handle, e)

                # Rate limiting: 1 second between requests
                if i < len(all_mapped) - 1:
                    await asyncio.sleep(1)

    if not all_mapped:
        logger.warning("No paddle products found on JOOLA Brazil")
        return 0

    async with get_connection() as conn:
        # retailer_id=2 is JOOLA (formerly Mercado Livre slot)
        saved = await save_products_to_db(all_mapped, retailer_id=2, conn=conn)
        await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices")
        await conn.commit()

    logger.info("Saved %d JOOLA products to price_snapshots", saved)
    return saved


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_joola_crawler())
