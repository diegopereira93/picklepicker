import os
import json
import logging
from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pipeline.db.connection import get_connection
from pipeline.alerts.telegram import send_telegram_alert
from pipeline.utils.security import scrub_sensitive_data, SensitiveDataFilter

logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

DROPSHOT_BRASIL_URL = "https://www.dropshotbrasil.com.br/raquetes"

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
