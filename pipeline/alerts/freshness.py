"""Data freshness monitoring and alerting module.

Checks if data from crawlers is fresh and sends alerts when data becomes stale.
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from pipeline.db.connection import get_connection
from pipeline.alerts.telegram import send_telegram_alert

logger = logging.getLogger(__name__)

FRESHNESS_THRESHOLD_HOURS = 48


async def get_latest_scrape_timestamp(source: str) -> Optional[datetime]:
    """Get the most recent scrape timestamp for a source.

    Args:
        source: Name of the data source (retailer name)

    Returns:
        Most recent scraped_at timestamp, or None if no data exists
    """
    async with get_connection() as conn:
        result = await conn.execute(
            """
            SELECT MAX(scraped_at) as latest
            FROM price_snapshots
            WHERE retailer_id = (
                SELECT id FROM retailers WHERE name = %(source)s
            )
            """,
            {"source": source},
        )
        row = await result.fetchone()
        return row[0] if row and row[0] else None


async def check_data_freshness() -> dict[str, bool]:
    """Check freshness for all data sources.

    Returns a map of source -> is_fresh boolean.
    Sends Telegram alerts for stale sources.

    Returns:
        Dict mapping source name to freshness boolean
    """
    sources = ["brazil_pickleball_store", "mercado_livre", "dropshot_brasil"]
    results = {}
    threshold = timedelta(hours=FRESHNESS_THRESHOLD_HOURS)

    for source in sources:
        latest = await get_latest_scrape_timestamp(source)
        if latest is None:
            results[source] = False
            await send_freshness_alert(source, None)
            logger.warning(f"No data found for source: {source}")
        elif datetime.now(timezone.utc) - latest.replace(tzinfo=timezone.utc) if latest.tzinfo is None else latest > threshold:
            results[source] = False
            await send_freshness_alert(source, latest)
            logger.warning(f"Stale data detected for {source}: {latest}")
        else:
            results[source] = True
            logger.info(f"Data for {source} is fresh (last updated: {latest})")

    return results


async def send_freshness_alert(source: str, latest: Optional[datetime]) -> None:
    """Send Telegram alert for stale data.

    Args:
        source: Name of the data source with stale data
        latest: Timestamp of most recent data, or None if no data exists
    """
    if latest is None:
        message = f"⚠️ Data Freshness Alert: No data found for {source}. Run crawlers immediately."
    else:
        # Ensure both datetimes are timezone-aware for comparison
        if latest.tzinfo is None:
            latest = latest.replace(tzinfo=timezone.utc)
        hours_old = int((datetime.now(timezone.utc) - latest).total_seconds() / 3600)
        message = f"⚠️ Data Freshness Alert: {source} data is {hours_old}h old (threshold: {FRESHNESS_THRESHOLD_HOURS}h)"

    await send_telegram_alert(message)
    logger.info(f"Sent freshness alert for {source}")
