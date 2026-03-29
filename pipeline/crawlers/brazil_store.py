import os
import json
import logging
from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pipeline.db.connection import get_connection
from pipeline.alerts.telegram import send_telegram_alert

logger = logging.getLogger(__name__)

BRAZIL_STORE_URL = "https://brazilpickleballstore.com.br/raquete/"

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


async def save_products_to_db(products: list[dict], retailer_id: int, conn) -> int:
    """Save extracted products to price_snapshots.

    Skips items without price_brl. Returns count of saved rows.
    paddle_id is left NULL in this phase — dedup/matching is Phase 2.
    """
    saved = 0
    for product in products:
        price = product.get("price_brl")
        if price is None:
            logger.warning(
                "Skipping product %s: missing price_brl", product.get("name", "unknown")
            )
            continue

        await conn.execute(
            """
            INSERT INTO price_snapshots
                (paddle_id, retailer_id, price_brl, currency, in_stock, affiliate_url, scraped_at, source_raw)
            VALUES
                (%(paddle_id)s, %(retailer_id)s, %(price_brl)s, 'BRL', %(in_stock)s, %(affiliate_url)s, NOW(), %(source_raw)s)
            """,
            {
                "paddle_id": None,
                "retailer_id": retailer_id,
                "price_brl": price,
                "in_stock": product.get("in_stock", False),
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
