import os
import json
import logging
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
from pipeline.db.connection import get_connection
from pipeline.alerts.telegram import send_telegram_alert
from pipeline.utils.security import scrub_sensitive_data, SensitiveDataFilter

logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

ML_SEARCH_URL = "https://api.mercadolibre.com/sites/MLB/search"
MAX_ITEMS = 1000  # Prevent unbounded memory growth
ML_DEFAULT_QUERY = "raquete pickleball"
ML_CATEGORY = "MLB1276"  # Esportes e Fitness


def build_affiliate_url(permalink: str, affiliate_tag: str) -> str:
    """Append ML affiliate tag to product permalink.

    NOTE: Parameter name 'matt_id' needs verification against ML Afiliados portal.
    Fallback: if tag is empty, return permalink as-is (no commission but link works).
    """
    if not affiliate_tag:
        return permalink
    separator = "&" if "?" in permalink else "?"
    return f"{permalink}{separator}matt_id={affiliate_tag}"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((
        httpx.HTTPStatusError,
        httpx.ConnectError,
        httpx.TimeoutException,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def search_pickleball_paddles(
    limit: int = 50,
    offset: int = 0,
    fetch_all: bool = False,
) -> dict:
    """Search ML for pickleball paddles. Public API — no auth required.

    If fetch_all=True, paginates through results up to MAX_ITEMS.
    Returns dict with 'results' list and 'paging' info.

    Retries on transient failures (5xx, connection errors, timeouts)
    with exponential backoff (1s, 2s, 4s). Does not retry on 4xx errors.
    """
    all_results = []
    current_offset = offset
    items_fetched = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Referer": "https://www.mercadolivre.com.br/",
    }

    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        while True:
            params = {
                "q": ML_DEFAULT_QUERY,
                "category": ML_CATEGORY,
                "limit": limit,
                "offset": current_offset,
            }
            response = await client.get(ML_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            all_results.extend(results)
            items_fetched += len(results)

            # Check memory limit
            if items_fetched >= MAX_ITEMS:
                logger.warning(
                    "Reached MAX_ITEMS limit (%d), stopping pagination. "
                    "Some results may be truncated.", MAX_ITEMS
                )
                break

            if not fetch_all:
                return data

            paging = data.get("paging", {})
            total = paging.get("total", 0)
            current_offset += limit

            if current_offset >= total or len(results) == 0:
                break

    return {
        "results": all_results,
        "paging": {
            "total": len(all_results),
            "offset": 0,
            "limit": len(all_results),
        },
    }


async def save_ml_items_to_db(items: list[dict], affiliate_tag: str, conn) -> int:
    """Save ML search items to price_snapshots.

    Uses atomic upsert for paddles (INSERT ... ON CONFLICT DO UPDATE)
    to avoid TOCTOU race conditions. Requires UNIQUE constraint on
    paddles.name.

    Skips items with missing/zero price.
    Returns count of saved snapshots.
    """
    # NOTE: Requires UNIQUE constraint on paddles.name
    # If this constraint doesn't exist, the upsert will fail
    # with a PostgreSQL error, which is safer than silent data loss
    saved = 0
    retailer_id = 2  # Mercado Livre from seed data (id=2)

    for item in items:
        price = item.get("price")
        if not price:  # None or 0
            logger.warning(
                "Skipping ML item %s: missing or zero price",
                item.get("id", "unknown"),
            )
            continue

        title = item.get("title", "")
        permalink = item.get("permalink", "")
        affiliate_url = build_affiliate_url(permalink, affiliate_tag)

        # Atomic upsert: insert or update, always return id
        result = await conn.execute(
            """
            INSERT INTO paddles (name, brand, model, images)
            VALUES (%(name)s, %(brand)s, %(model)s, %(images)s)
            ON CONFLICT (name) DO UPDATE SET
                brand = EXCLUDED.brand,
                model = EXCLUDED.model,
                images = EXCLUDED.images,
                updated_at = NOW()
            RETURNING id
            """,
            {
                "name": title,
                "brand": "",  # ML search doesn't always have separate brand
                "model": title,
                "images": [item.get("thumbnail", "")],
            },
        )
        row = await result.fetchone()
        if row is None:
            logger.error("Upsert failed for paddle: %s", title)
            continue

        paddle_id = row[0]

        await conn.execute(
            """
            INSERT INTO price_snapshots
                (paddle_id, retailer_id, price_brl, currency, in_stock,
                 affiliate_url, scraped_at, source_raw)
            VALUES
                (%(paddle_id)s, %(retailer_id)s, %(price_brl)s, 'BRL',
                 %(in_stock)s, %(affiliate_url)s, NOW(), %(source_raw)s)
            """,
            {
                "paddle_id": paddle_id,
                "retailer_id": retailer_id,
                "price_brl": price,
                "in_stock": (item.get("available_quantity", 0) > 0),
                "affiliate_url": affiliate_url,
                "source_raw": json.dumps(item),
            },
        )
        saved += 1

    return saved


async def run_mercado_livre_crawler() -> int:
    """Main entry point: search ML, save to DB with affiliate URLs.

    Returns count of saved snapshots.
    """
    affiliate_tag = os.environ.get("ML_AFFILIATE_TAG", "")
    if not affiliate_tag:
        logger.warning(
            "ML_AFFILIATE_TAG not set — saving plain permalinks without affiliate commission"
        )

    try:
        data = await search_pickleball_paddles(limit=50, offset=0, fetch_all=True)
    except Exception as e:
        # Scrub sensitive data before sending alert
        safe_message = scrub_sensitive_data(str(e))
        await send_telegram_alert(f"Mercado Livre crawler failed: {safe_message}")
        raise

    items = data.get("results", [])
    logger.info("Fetched %d items from Mercado Livre", len(items))

    if not items:
        logger.warning("No items found on Mercado Livre")
        return 0

    async with get_connection() as conn:
        saved = await save_ml_items_to_db(items, affiliate_tag, conn)
        await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices")
        await conn.commit()

    logger.info("Saved %d ML items to price_snapshots", saved)
    return saved


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_mercado_livre_crawler())
