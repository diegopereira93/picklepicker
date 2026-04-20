"""Price history endpoint with P20 percentile calculation."""

import logging
from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Query
from psycopg.rows import dict_row
from app.db import get_connection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/paddles", tags=["paddles"])


def calculate_p20(prices: list[float]) -> float:
    """Calculate the 20th percentile of a list of prices.

    Uses floor(n * 0.2) index into sorted array.
    Returns the minimum price if index is 0.
    """
    if not prices:
        raise ValueError("Cannot calculate P20 of empty price list")
    sorted_prices = sorted(prices)
    idx = int(len(sorted_prices) * 0.2)
    # idx=0 returns minimum price (still valid — it's the lowest)
    return sorted_prices[idx]


def group_prices_by_retailer(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Group price snapshot rows by retailer and calculate P20 per retailer.

    Args:
        rows: List of dicts with keys: retailer_name, price_brl, date

    Returns:
        List of dicts with keys: retailer, date, price, p20, is_good_time
    """
    if not rows:
        return []

    # Group prices per retailer
    retailer_prices: dict[str, list[float]] = {}
    retailer_points: dict[str, list[dict]] = {}

    for row in rows:
        retailer = row["retailer_name"]
        price = float(row["price_brl"])
        date_val = row["date"]
        # Normalize date to ISO string
        if hasattr(date_val, "isoformat"):
            date_str = date_val.isoformat()
        else:
            date_str = str(date_val)

        if retailer not in retailer_prices:
            retailer_prices[retailer] = []
            retailer_points[retailer] = []

        retailer_prices[retailer].append(price)
        retailer_points[retailer].append({"date": date_str, "price": price})

    # Calculate P20 per retailer, then annotate each point
    result = []
    for retailer, points in retailer_points.items():
        p20 = calculate_p20(retailer_prices[retailer])
        for point in points:
            result.append(
                {
                    "retailer": retailer,
                    "date": point["date"],
                    "price": point["price"],
                    "p20": p20,
                    "is_good_time": point["price"] <= p20,
                }
            )

    return result


@router.get("/{paddle_id}/price-history")
async def get_price_history(
    paddle_id: int,
    days: int = Query(90, ge=1, le=180, description="Number of days of history (1–180)"),
):
    """Get price history for a paddle with P20 percentile indicator.

    Returns price snapshots for the last N days, grouped by retailer,
    with a 20th-percentile indicator ('is_good_time') per retailer.
    """
    cutoff_date = datetime.now() - timedelta(days=days)

    query = """
        SELECT
            ps.retailer_id,
            ps.price_brl,
            ps.scraped_at::date AS date,
            r.name AS retailer_name
        FROM price_snapshots ps
        JOIN retailers r ON r.id = ps.retailer_id
        WHERE ps.paddle_id = %s
          AND ps.scraped_at >= %s
        ORDER BY ps.retailer_id, ps.scraped_at ASC
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, [paddle_id, cutoff_date])
            rows = await cur.fetchall()
            rows = [dict(r) for r in rows]

    return group_prices_by_retailer(rows)
