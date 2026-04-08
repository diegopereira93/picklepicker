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

logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

DROPSHOT_BRASIL_URL = "https://www.dropshotbrasil.com.br/raquetes"


def normalize_paddle_name(name: str) -> str:
    if not name:
        return ""
    normalized = name.lower().strip()
    normalized = re.sub(r'\s+', ' ', normalized)
    for prefix in ['raquete ', 'raquete']:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
    for old in ['pickleball', 'de pickleball', 'para pickleball']:
        normalized = normalized.replace(old, '')
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

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


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def extract_products(app: FirecrawlApp, url: str) -> dict:
    """Extract paddle products from URL using Firecrawl /extract endpoint."""
    return app.extract(
        urls=[url],
        prompt=(
            "Extract all pickleball paddle products with name, price in BRL, "
            "availability, image URL, product URL, brand, and technical specs"
        ),
        schema=FIRECRAWL_SCHEMA,
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def scrape_product_page(app: FirecrawlApp, url: str) -> Optional[str]:
    """Scrape individual product page and extract image URL."""
    try:
        result = app.scrape(url)
        if hasattr(result, 'markdown'):
            markdown = result.markdown
        elif isinstance(result, dict):
            markdown = result.get('markdown', '')
        else:
            return None
        return extract_image_from_markdown(markdown)
    except Exception as e:
        logger.warning(f"Failed to scrape product page {url}: {e}")
        return None


def extract_image_from_markdown(markdown: str) -> Optional[str]:
    """Extract image URL from markdown content using regex.
    
    Handles Dropshot Brasil CDN patterns.
    """
    pattern = r'!\[.*?\]\((https?://[^)]+\.(?:jpg|jpeg|png|webp))\)'
    matches = re.findall(pattern, markdown, re.IGNORECASE)
    
    cdn_patterns = [
        'dropshot.com.br',
        'dropshotbrasil.com.br',
        'cloudfront.net',
        'amazonaws.com',
        'cdn',
    ]
    
    for match in matches:
        if any(cdn in match.lower() for cdn in cdn_patterns):
            return match
    
    # Fallback: return first match if it looks like a product image
    if matches and len(matches[0]) > 80:
        return matches[0]
    
    return None


async def save_products_to_db(products: list[dict], retailer_id: int, conn) -> int:
    """Save extracted products to paddles + price_snapshots.

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

        result = await conn.execute(
            """
            INSERT INTO paddles (name, brand, model, image_url, in_stock, price_min_brl)
            VALUES (%(name)s, %(brand)s, %(model)s, %(image_url)s, %(in_stock)s, %(price_min_brl)s)
            ON CONFLICT (name) DO UPDATE SET
                brand = EXCLUDED.brand,
                model = EXCLUDED.model,
                image_url = COALESCE(NULLIF(EXCLUDED.image_url, ''), paddles.image_url),
                in_stock = EXCLUDED.in_stock,
                price_min_brl = LEAST(paddles.price_min_brl, EXCLUDED.price_min_brl),
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
            },
        )
        row = await result.fetchone()
        if row is None:
            logger.error("Upsert failed for paddle: %s", name)
            continue

        paddle_id = row[0]

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


def validate_image_belongs_to_product(image_url: str, product_name: str) -> bool:
    if not image_url or not product_name:
        return False

    skip_words = {'the', 'and', 'or', 'de', 'do', 'da', 'em', 'um', 'uma', 'raquete', 'pickleball'}
    keywords = [w.lower() for w in product_name.split() if w.lower() not in skip_words and len(w) > 2]
    
    image_lower = image_url.lower()
    matching_keywords = [kw for kw in keywords if kw in image_lower]
    if matching_keywords:
        return True
    
    cdn_domains = ['mitiendanube.com', 'cloudfront.net', 'amazonaws.com', 'dropshotbrasil.com.br']
    has_valid_extension = any(ext in image_lower for ext in ['.jpg', '.jpeg', '.png', '.webp'])
    is_known_cdn = any(domain in image_lower for domain in cdn_domains)
    has_reasonable_length = len(image_url) > 60
    
    return is_known_cdn and has_valid_extension and has_reasonable_length


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
        # Scrub any sensitive data from error message before logging/alerting
        safe_message = scrub_sensitive_data(str(e))
        logger.error("Drop Shot Brasil crawler failed: %s", safe_message)
        await send_telegram_alert(
            f"Drop Shot Brasil crawler failed after 3 retries: {safe_message}"
        )
        # Re-raise sanitized exception
        raise type(e)(safe_message) from e

    # Convert ExtractResponse to dict if needed
    if hasattr(result, 'model_dump'):
        result = result.model_dump()
    elif hasattr(result, 'dict'):
        result = result.dict()

    products = (result.get("data") or {}).get("products", [])
    logger.info("Extracted %d products from Drop Shot Brasil", len(products))

    # Phase 2: Scrape individual product pages for better images
    logger.info("Starting Phase 2: Scraping individual product pages for images...")
    for i, product in enumerate(products):
        product_url = product.get("product_url") or product.get("url")
        current_image = product.get("image_url", "")
        product_name = product.get("name", "")

        if product_url:
            logger.debug(f"Scraping product page {i+1}/{len(products)}: {product_url}")
            phase2_image = scrape_product_page(app, product_url)
            
            if phase2_image:
                should_replace = False
                
                if not current_image:
                    should_replace = True
                elif "placeholder" in current_image.lower():
                    should_replace = True
                elif len(phase2_image) > len(current_image) + 20:
                    should_replace = True
                
                # NEW: Validate image belongs to product before replacing
                if should_replace and not validate_image_belongs_to_product(phase2_image, product_name):
                    logger.warning(f"Phase 2 image for '{product_name[:40]}' may not belong to product: {phase2_image[:60]}...")
                    # Still use it if current image is placeholder or empty
                    if not current_image or "placeholder" in current_image.lower():
                        pass  # Use it anyway
                    else:
                        should_replace = False  # Keep current image

                if should_replace:
                    product["image_url"] = phase2_image
                    logger.info(
                        f"Phase 2 image for '{product_name[:40]}...': {phase2_image[:60]}..."
                    )
            
            if i < len(products) - 1:
                time.sleep(1)

    products_with_images = [p for p in products if p.get("image_url")]
    logger.info(f"Phase 2 complete: {len(products_with_images)}/{len(products)} products have images")

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
