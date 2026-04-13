"""Price Alerts API endpoints."""

import logging
from fastapi import APIRouter, HTTPException, Query, status
from psycopg.rows import dict_row
from app.schemas import PriceAlertCreate, PriceAlertResponse
from app.db import get_connection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/price-alerts", tags=["price-alerts"])


@router.post("", response_model=PriceAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_price_alert(alert: PriceAlertCreate):
    """Create a new price alert.

    Checks for duplicate alerts (same user_id + paddle_id with is_active=true)
    and returns 409 Conflict if one exists.
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            duplicate_check = """
                SELECT id FROM price_alerts
                WHERE user_id = %s AND paddle_id = %s AND is_active = TRUE
            """
            await cur.execute(duplicate_check, [alert.user_id, alert.paddle_id])
            existing = await cur.fetchone()

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Price alert already exists for this user and paddle"
                )

            insert_query = """
                INSERT INTO price_alerts (user_id, paddle_id, target_price_brl, is_active)
                VALUES (%s, %s, %s, TRUE)
                RETURNING id, user_id, paddle_id, target_price_brl, is_active, created_at
            """
            await cur.execute(
                insert_query,
                [alert.user_id, alert.paddle_id, alert.target_price_brl]
            )
            result = await cur.fetchone()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create price alert"
                )

    return PriceAlertResponse(**result)


@router.get("", response_model=list[PriceAlertResponse], status_code=status.HTTP_200_OK)
async def list_price_alerts(user_id: int = Query(..., description="Filter by user ID")):
    """List all price alerts for a specific user."""
    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            query = """
                SELECT id, user_id, paddle_id, target_price_brl, is_active, created_at
                FROM price_alerts
                WHERE user_id = %s
                ORDER BY created_at DESC
            """
            await cur.execute(query, [user_id])
            alerts = await cur.fetchall()

    return [PriceAlertResponse(**alert) for alert in alerts]
