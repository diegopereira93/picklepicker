"""Tests for dead letter queue module.

TDD RED phase: Write failing tests for dead letter queue.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from pipeline.db.dead_letter_queue import (
    DLQStatus,
    DeadLetterItem,
    queue_failed_extraction,
    get_pending_dlq_items,
    update_dlq_status,
    retry_dead_letter_items,
)


class TestDLQStatus:
    """Test DLQStatus enum."""

    def test_status_values(self):
        """Should have expected status values."""
        assert DLQStatus.PENDING.value == "pending"
        assert DLQStatus.PROCESSING.value == "processing"
        assert DLQStatus.RESOLVED.value == "resolved"
        assert DLQStatus.FAILED.value == "failed"


class TestDeadLetterItem:
    """Test DeadLetterItem Pydantic model."""

    def test_create_dead_letter_item(self):
        """Should create a dead letter item with defaults."""
        item = DeadLetterItem(
            source="dropshot_brasil",
            payload={"name": "Test Paddle", "price": 100},
            error_message="Connection timeout",
        )
        assert item.source == "dropshot_brasil"
        assert item.payload == {"name": "Test Paddle", "price": 100}
        assert item.error_message == "Connection timeout"
        assert item.retry_count == 0
        assert item.max_retries == 3
        assert item.status == DLQStatus.PENDING
        assert isinstance(item.created_at, datetime)

    def test_dead_letter_item_with_custom_retries(self):
        """Should allow custom max_retries."""
        item = DeadLetterItem(
            source="mercado_livre",
            payload={},
            error_message="API error",
            max_retries=5,
        )
        assert item.max_retries == 5


class TestQueueFailedExtraction:
    """Test queue_failed_extraction function."""

    @pytest.mark.asyncio
    async def test_queue_failed_extraction_inserts_to_db(self):
        """Should insert failed extraction into DLQ."""
        mock_conn = AsyncMock()
        mock_cursor = AsyncMock()
        mock_cursor.fetchone.return_value = (42,)  # Return ID
        mock_conn.execute.return_value = mock_cursor

        with patch("pipeline.db.dead_letter_queue.get_connection") as mock_get_conn:
            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            item_id = await queue_failed_extraction(
                source="dropshot_brasil",
                payload={"url": "https://example.com"},
                error_message="Timeout",
            )

            assert item_id == 42
            mock_conn.execute.assert_called_once()
            call_args = mock_conn.execute.call_args
            sql = call_args[0][0]
            assert "INSERT INTO dead_letter_queue" in sql
            params = call_args[0][1]
            assert params["source"] == "dropshot_brasil"
            assert json.loads(params["payload"]) == {"url": "https://example.com"}


class TestGetPendingDLQItems:
    """Test get_pending_dlq_items function."""

    @pytest.mark.asyncio
    async def test_get_pending_dlq_items_returns_list(self):
        """Should return list of pending DeadLetterItem objects."""
        mock_conn = AsyncMock()
        mock_result = AsyncMock()
        # psycopg returns tuples: (id, source, payload, error_message, retry_count, max_retries, status, created_at, updated_at)
        mock_row = (
            1,
            "dropshot_brasil",
            '{"name": "Test"}',
            "Error message",
            0,
            3,
            "pending",
            datetime.utcnow(),
            None,
        )
        mock_result.fetchall.return_value = [mock_row]
        mock_conn.execute.return_value = mock_result

        with patch("pipeline.db.dead_letter_queue.get_connection") as mock_get_conn:
            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            items = await get_pending_dlq_items(limit=100)

            assert isinstance(items, list)
            assert len(items) == 1
            assert isinstance(items[0], DeadLetterItem)
            assert items[0].id == 1
            assert items[0].source == "dropshot_brasil"

    @pytest.mark.asyncio
    async def test_get_pending_dlq_items_respects_limit(self):
        """Should respect the limit parameter."""
        mock_conn = AsyncMock()

        with patch("pipeline.db.dead_letter_queue.get_connection") as mock_get_conn:
            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            await get_pending_dlq_items(limit=50)

            call_args = mock_conn.execute.call_args
            params = call_args[0][1]
            assert params["limit"] == 50


class TestUpdateDLQStatus:
    """Test update_dlq_status function."""

    @pytest.mark.asyncio
    async def test_update_dlq_status_changes_status(self):
        """Should update status without incrementing retry."""
        mock_conn = AsyncMock()

        with patch("pipeline.db.dead_letter_queue.get_connection") as mock_get_conn:
            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            await update_dlq_status(1, DLQStatus.RESOLVED)

            mock_conn.execute.assert_called_once()
            call_args = mock_conn.execute.call_args
            params = call_args[0][1]
            assert params["status"] == "resolved"
            assert params["increment"] == 0

    @pytest.mark.asyncio
    async def test_update_dlq_status_increments_retry(self):
        """Should increment retry count when requested."""
        mock_conn = AsyncMock()

        with patch("pipeline.db.dead_letter_queue.get_connection") as mock_get_conn:
            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            await update_dlq_status(1, DLQStatus.PROCESSING, increment_retry=True)

            call_args = mock_conn.execute.call_args
            params = call_args[0][1]
            assert params["status"] == "processing"
            assert params["increment"] == 1


class TestRetryDeadLetterItems:
    """Test retry_dead_letter_items function."""

    @pytest.mark.asyncio
    async def test_retry_processes_pending_items(self):
        """Should process pending items and update status."""
        mock_conn = AsyncMock()

        with patch("pipeline.db.dead_letter_queue.get_connection") as mock_get_conn, \
             patch("pipeline.db.dead_letter_queue.get_pending_dlq_items") as mock_get_pending, \
             patch("pipeline.db.dead_letter_queue.update_dlq_status") as mock_update:

            mock_get_cm = AsyncMock()
            mock_get_cm.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_get_cm.__aexit__ = AsyncMock(return_value=False)
            mock_get_conn.return_value = mock_get_cm

            # Create mock items
            mock_item = DeadLetterItem(
                id=1,
                source="dropshot_brasil",
                payload={"url": "https://example.com"},
                error_message="Timeout",
                retry_count=0,
                max_retries=3,
                status=DLQStatus.PENDING,
                created_at=datetime.utcnow(),
            )
            mock_get_pending.return_value = [mock_item]
            mock_update.return_value = None

            results = await retry_dead_letter_items(limit=10)

            assert results["processed"] == 1
            mock_get_pending.assert_called_once_with(limit=10)

    @pytest.mark.asyncio
    async def test_retry_handles_empty_queue(self):
        """Should handle empty queue gracefully."""
        with patch("pipeline.db.dead_letter_queue.get_pending_dlq_items") as mock_get_pending:
            mock_get_pending.return_value = []

            results = await retry_dead_letter_items()

            assert results["processed"] == 0
            assert results["resolved"] == 0
            assert results["failed"] == 0
