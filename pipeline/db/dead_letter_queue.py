"""Dead letter queue module for failed extraction handling.

Provides storage and retry capabilities for failed crawler extractions.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel

from pipeline.db.connection import get_connection

logger = logging.getLogger(__name__)


class DLQStatus(str, Enum):
    """Status values for dead letter queue items."""

    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    FAILED = "failed"  # Max retries exceeded


class DeadLetterItem(BaseModel):
    """Represents a failed extraction in the dead letter queue.

    Attributes:
        id: Unique identifier for the DLQ item
        source: Which crawler produced the failure
        payload: The data that failed to process (stored as JSON)
        error_message: Error that caused the failure
        retry_count: Number of retry attempts made
        max_retries: Maximum number of retry attempts allowed
        status: Current status of the item
        created_at: When the item was added to DLQ
        updated_at: When the item was last updated
    """

    id: Optional[int] = None
    source: str
    payload: dict
    error_message: str
    retry_count: int = 0
    max_retries: int = 3
    status: DLQStatus = DLQStatus.PENDING
    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None


async def queue_failed_extraction(
    source: str,
    payload: dict,
    error_message: str,
    max_retries: int = 3,
) -> int:
    """Add a failed extraction to the DLQ.

    Args:
        source: Name of the crawler that failed
        payload: The data that failed to process
        error_message: Description of the failure
        max_retries: Maximum retry attempts (default: 3)

    Returns:
        The ID of the created DLQ item
    """
    async with get_connection() as conn:
        result = await conn.execute(
            """
            INSERT INTO dead_letter_queue
                (source, payload, error_message, max_retries, status, created_at)
            VALUES (%(source)s, %(payload)s, %(error_message)s, %(max_retries)s, 'pending', NOW())
            RETURNING id
            """,
            {
                "source": source,
                "payload": json.dumps(payload),
                "error_message": error_message,
                "max_retries": max_retries,
            },
        )
        row = await result.fetchone()
        await conn.commit()
        item_id = row[0]
        logger.info(f"Added item {item_id} to DLQ for source: {source}")
        return item_id


async def get_pending_dlq_items(limit: int = 100) -> list[DeadLetterItem]:
    """Get pending DLQ items for retry processing.

    Retrieves items that are pending and have not exceeded max retries.

    Args:
        limit: Maximum number of items to retrieve

    Returns:
        List of DeadLetterItem objects ready for retry
    """
    async with get_connection() as conn:
        result = await conn.execute(
            """
            SELECT id, source, payload, error_message, retry_count, max_retries, status, created_at, updated_at
            FROM dead_letter_queue
            WHERE status = 'pending' AND retry_count < max_retries
            ORDER BY created_at
            LIMIT %(limit)s
            """,
            {"limit": limit},
        )
        rows = await result.fetchall()
        items = []
        for row in rows:
            item_data = {
                "id": row[0],
                "source": row[1],
                "payload": json.loads(row[2]),
                "error_message": row[3],
                "retry_count": row[4],
                "max_retries": row[5],
                "status": DLQStatus(row[6]),
                "created_at": row[7],
                "updated_at": row[8],
            }
            items.append(DeadLetterItem(**item_data))
        return items


async def update_dlq_status(
    item_id: int,
    status: DLQStatus,
    increment_retry: bool = False,
) -> None:
    """Update DLQ item status and optionally increment retry count.

    Args:
        item_id: ID of the DLQ item to update
        status: New status to set
        increment_retry: Whether to increment the retry_count
    """
    async with get_connection() as conn:
        await conn.execute(
            """
            UPDATE dead_letter_queue
            SET status = %(status)s,
                retry_count = retry_count + %(increment)s,
                updated_at = NOW()
            WHERE id = %(id)s
            """,
            {"status": status.value, "increment": 1 if increment_retry else 0, "id": item_id},
        )
        await conn.commit()
        logger.debug(f"Updated DLQ item {item_id} to status: {status.value}")


async def retry_dead_letter_items(limit: int = 100) -> dict:
    """Process pending DLQ items with retry logic.

    This is a coordinator function that retrieves pending items and
    marks them for retry. The actual reprocessing logic should be
    implemented by the caller based on the source type.

    Args:
        limit: Maximum number of items to process

    Returns:
        Dict with processed, resolved, and failed counts
    """
    items = await get_pending_dlq_items(limit=limit)
    results = {"processed": 0, "resolved": 0, "failed": 0}

    for item in items:
        results["processed"] += 1

        # Mark as processing
        await update_dlq_status(item.id, DLQStatus.PROCESSING, increment_retry=True)

        # Check if max retries exceeded
        if item.retry_count + 1 >= item.max_retries:
            await update_dlq_status(item.id, DLQStatus.FAILED)
            results["failed"] += 1
            logger.warning(
                f"DLQ item {item.id} from {item.source} exceeded max retries"
            )
        else:
            # Item is ready for retry - actual retry logic is source-specific
            # and should be implemented by the caller
            results["resolved"] += 1
            logger.info(f"DLQ item {item.id} from {item.source} ready for retry")

    return results
