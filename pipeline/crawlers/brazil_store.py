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
                    "specs": {"type": "object"},
                },
            },
        }
    },
}


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=10, max=120),
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


def extract_image_from_markdown(markdown: str) -> Optional[str]:
    """Extract image URL from markdown content using regex.

    Looks for mitiendanube.com CDN URLs and transforms them to smaller size.
    """
    pattern = r'!\[.*?\]\((https?://[^)]+\.(?:jpg|jpeg|png|webp))\)'
    matches = re.findall(pattern, markdown, re.IGNORECASE)
    for match in matches:
        if 'mitiendanube.com' in match:
            return match.replace('-1024-1024', '-480-0')
    return None


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

        name = product.get("name", "")
        brand = product.get("brand", "")
        image_url = product.get("image_url", "")

        # Atomic upsert: insert or update paddle, always return id
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

    # Phase 2: Scrape individual product pages for images
    logger.info("Starting Phase 2: Scraping individual product pages for images...")
    for i, product in enumerate(products):
        product_url = product.get("product_url") or product.get("url")
        current_image = product.get("image_url", "")

        # Only scrape if we have a product URL and no/placeholder image
        if product_url and (not current_image or "placeholder" in current_image.lower()):
            logger.debug(f"Scraping product page {i+1}/{len(products)}: {product_url}")
            image_url = scrape_product_page(app, product_url)
            if image_url:
                product["image_url"] = image_url
                logger.info(f"Found image for '{product.get('name', 'Unknown')[:40]}...': {image_url[:60]}...")
            # Rate limiting: sleep between scrapes
            if i < len(products) - 1:
                time.sleep(1)

    # Count products with images
    products_with_images = [p for p in products if p.get("image_url")]
    logger.info(f"Phase 2 complete: {len(products_with_images)}/{len(products)} products have images")

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
