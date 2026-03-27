"""Review queue management for flagged deduplication items."""

import json
import logging
from datetime import datetime
from pipeline.db.connection import get_connection

logger = logging.getLogger(__name__)

QUEUE_TYPES = {
    "duplicate": "Potential duplicate paddles detected",
    "spec_unmatched": "Specs could not be matched to catalog",
    "price_anomaly": "Unusual price detected",
}


async def add_to_review_queue(
    queue_type: str,
    paddle_id: int,
    related_paddle_id: int | None = None,
    data: dict | None = None,
) -> int:
    """Add item to review queue for manual verification.

    Args:
        queue_type: Type of issue (duplicate, spec_unmatched, price_anomaly)
        paddle_id: Primary paddle ID
        related_paddle_id: Secondary paddle ID (for duplicates)
        data: Extra context (match score, suggestion, etc.)

    Returns:
        review_queue item ID
    """
    if queue_type not in QUEUE_TYPES:
        raise ValueError(f"Invalid queue_type: {queue_type}. Must be one of {list(QUEUE_TYPES.keys())}")

    if data is None:
        data = {}

    async with get_connection() as conn:
        result = await conn.execute(
            """
            INSERT INTO review_queue
                (type, paddle_id, related_paddle_id, data, status, created_at)
            VALUES
                (%(type)s, %(paddle_id)s, %(related_paddle_id)s, %(data)s, 'pending', NOW())
            RETURNING id
            """,
            {
                "type": queue_type,
                "paddle_id": paddle_id,
                "related_paddle_id": related_paddle_id,
                "data": json.dumps(data),
            },
        )
        row = await result.fetchone()
        await conn.commit()

    queue_id = row[0] if row else None
    logger.info(
        f"Added to review_queue: type={queue_type}, paddle_id={paddle_id}, "
        f"related_paddle_id={related_paddle_id}, queue_id={queue_id}"
    )
    return queue_id


async def get_review_queue_items(
    queue_type: str | None = None,
    status: str = "pending",
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Retrieve items from review queue.

    Args:
        queue_type: Filter by type (optional)
        status: Filter by status (default: pending)
        limit: Max items to return
        offset: Pagination offset

    Returns:
        List of review queue items with paddle info
    """
    async with get_connection() as conn:
        if queue_type:
            result = await conn.execute(
                """
                SELECT id, type, paddle_id, related_paddle_id, data, status, created_at
                FROM review_queue
                WHERE type = %(type)s AND status = %(status)s
                ORDER BY created_at DESC
                LIMIT %(limit)s OFFSET %(offset)s
                """,
                {
                    "type": queue_type,
                    "status": status,
                    "limit": limit,
                    "offset": offset,
                },
            )
        else:
            result = await conn.execute(
                """
                SELECT id, type, paddle_id, related_paddle_id, data, status, created_at
                FROM review_queue
                WHERE status = %(status)s
                ORDER BY created_at DESC
                LIMIT %(limit)s OFFSET %(offset)s
                """,
                {
                    "status": status,
                    "limit": limit,
                    "offset": offset,
                },
            )
        rows = await result.fetchall()

    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "type": row[1],
            "paddle_id": row[2],
            "related_paddle_id": row[3],
            "data": json.loads(row[4]) if row[4] else {},
            "status": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
        })

    return items


async def resolve_queue_item(
    queue_id: int,
    action: str,
    resolved_by: str = "system",
    decision_data: dict | None = None,
) -> bool:
    """Mark review queue item as resolved.

    Args:
        queue_id: review_queue item ID
        action: Resolution action (merge, reject, manual, etc.)
        resolved_by: User or system that resolved it
        decision_data: Extra context about the decision

    Returns:
        True if successfully resolved, False if not found
    """
    if decision_data is None:
        decision_data = {}

    async with get_connection() as conn:
        # Get existing data
        result = await conn.execute(
            "SELECT data FROM review_queue WHERE id = %(id)s",
            {"id": queue_id}
        )
        row = await result.fetchone()

        if not row:
            logger.warning(f"review_queue item {queue_id} not found")
            return False

        existing_data = json.loads(row[0]) if row[0] else {}
        existing_data["action"] = action
        existing_data["resolved_by"] = resolved_by
        existing_data.update(decision_data)

        # Update item
        await conn.execute(
            """
            UPDATE review_queue
            SET status = 'resolved', data = %(data)s, resolved_at = NOW()
            WHERE id = %(id)s
            """,
            {
                "id": queue_id,
                "data": json.dumps(existing_data),
            },
        )
        await conn.commit()

    logger.info(f"Resolved review_queue item {queue_id}: action={action}")
    return True


async def dismiss_queue_item(queue_id: int, reason: str = "") -> bool:
    """Dismiss a review queue item (status=dismissed).

    Args:
        queue_id: review_queue item ID
        reason: Why it was dismissed

    Returns:
        True if successfully dismissed
    """
    async with get_connection() as conn:
        await conn.execute(
            """
            UPDATE review_queue
            SET status = 'dismissed', resolved_at = NOW(), data = jsonb_set(data, '{dismissal_reason}', %(reason)s)
            WHERE id = %(id)s
            """,
            {
                "id": queue_id,
                "reason": json.dumps(reason),
            },
        )
        await conn.commit()

    logger.info(f"Dismissed review_queue item {queue_id}")
    return True
