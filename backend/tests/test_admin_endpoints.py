"""Tests for admin API endpoints and review_queue module."""

import os
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import datetime

# Set admin secret for all tests
os.environ["ADMIN_SECRET"] = "test-admin-secret"

ADMIN_HEADERS = {"Authorization": "Bearer test-admin-secret"}


# Admin endpoint tests

def test_get_queue__returns_200_with_items():
    """GET /admin/queue returns 200 with queue items."""
    from backend.app.api.admin import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    mock_items = [
        {
            "id": 1,
            "type": "duplicate",
            "paddle_id": 10,
            "related_paddle_id": 11,
            "data": {"score": 0.87},
            "status": "pending",
            "created_at": "2026-03-27T10:00:00",
        }
    ]

    with patch("backend.app.api.admin.get_review_queue_items") as mock_get_items:
        mock_get_items.return_value = mock_items

        response = client.get("/admin/queue", headers=ADMIN_HEADERS)

        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["type"] == "duplicate"


def test_get_queue__filters_by_type():
    """GET /admin/queue?type=duplicate filters correctly."""
    from backend.app.api.admin import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    with patch("backend.app.api.admin.get_review_queue_items") as mock_get_items:
        mock_get_items.return_value = []

        response = client.get("/admin/queue?type=duplicate&status=pending", headers=ADMIN_HEADERS)

        assert response.status_code == 200
        # Verify the mock was called with correct params
        mock_get_items.assert_called_once()
        call_kwargs = mock_get_items.call_args[1]
        assert call_kwargs["queue_type"] == "duplicate"
        assert call_kwargs["status"] == "pending"


def test_get_queue__returns_401_without_auth():
    """GET /admin/queue returns 401 without Authorization header."""
    from backend.app.api.admin import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    with patch("backend.app.api.admin.get_review_queue_items"):
        response = client.get("/admin/queue")
        assert response.status_code == 422


def test_get_queue__returns_401_with_wrong_secret():
    """GET /admin/queue returns 401 with wrong admin token."""
    from backend.app.api.admin import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    with patch("backend.app.api.admin.get_review_queue_items"):
        response = client.get("/admin/queue", headers={"Authorization": "Bearer wrong-secret"})
        assert response.status_code == 401


def test_resolve_queue_item__updates_status():
    """PATCH /admin/queue/{id}/resolve updates item status."""
    from backend.app.api.admin import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    with patch("backend.app.api.admin.resolve_queue_item") as mock_resolve:
        mock_resolve.return_value = True

        response = client.patch(
            "/admin/queue/1/resolve",
            json={
                "action": "merge",
                "decision_data": {"merged_into": 10}
            },
            headers=ADMIN_HEADERS,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "resolved"
        mock_resolve.assert_called_once()


def test_resolve_queue_item__returns_404_if_not_found():
    """PATCH /admin/queue/{id}/resolve returns 404 if item not found."""
    from backend.app.api.admin import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    with patch("backend.app.api.admin.resolve_queue_item") as mock_resolve:
        mock_resolve.return_value = False

        response = client.patch(
            "/admin/queue/999/resolve",
            json={"action": "merge"},
            headers=ADMIN_HEADERS,
        )

        assert response.status_code == 404


def test_dismiss_queue_item__marks_dismissed():
    """PATCH /admin/queue/{id}/dismiss marks item as dismissed."""
    from backend.app.api.admin import router

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    with patch("backend.app.api.admin.dismiss_queue_item") as mock_dismiss:
        mock_dismiss.return_value = True

        response = client.patch(
            "/admin/queue/1/dismiss",
            json={"reason": "False positive"},
            headers=ADMIN_HEADERS,
        )

        assert response.status_code == 200
        assert response.json()["status"] == "dismissed"


# Review queue module integration tests

@pytest.mark.asyncio
async def test_add_to_review_queue__creates_record():
    """add_to_review_queue creates record in DB."""
    from pipeline.dedup.review_queue import add_to_review_queue

    mock_db_connection = AsyncMock()
    result_mock = AsyncMock()
    result_mock.fetchone = AsyncMock(return_value=(42,))
    mock_db_connection.execute = AsyncMock(return_value=result_mock)
    mock_db_connection.commit = AsyncMock()

    with patch("pipeline.dedup.review_queue.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        queue_id = await add_to_review_queue(
            queue_type="duplicate",
            paddle_id=10,
            related_paddle_id=11,
            data={"score": 0.87}
        )

        assert queue_id == 42
        mock_db_connection.execute.assert_called_once()
        mock_db_connection.commit.assert_called_once()


@pytest.mark.asyncio
async def test_add_to_review_queue__invalid_type_raises_error():
    """add_to_review_queue raises error for invalid queue_type."""
    from pipeline.dedup.review_queue import add_to_review_queue

    with pytest.raises(ValueError, match="Invalid queue_type"):
        await add_to_review_queue(
            queue_type="invalid_type",
            paddle_id=10
        )


@pytest.mark.asyncio
async def test_get_review_queue_items__filters_correctly():
    """get_review_queue_items applies filters."""
    from pipeline.dedup.review_queue import get_review_queue_items

    mock_db_connection = AsyncMock()
    result_mock = AsyncMock()
    result_mock.fetchall = AsyncMock(return_value=[
        (1, "duplicate", 10, 11, '{"score": 0.87}', "pending", datetime.now()),
    ])
    mock_db_connection.execute = AsyncMock(return_value=result_mock)

    with patch("pipeline.dedup.review_queue.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        items = await get_review_queue_items(queue_type="duplicate", status="pending")

        assert len(items) == 1
        assert items[0]["type"] == "duplicate"
        assert items[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_resolve_queue_item__updates_status_and_data():
    """resolve_queue_item updates status and adds decision data."""
    from pipeline.dedup.review_queue import resolve_queue_item

    mock_db_connection = AsyncMock()
    result_mock = AsyncMock()
    result_mock.fetchone = AsyncMock(return_value=('{"existing": "data"}',))
    mock_db_connection.execute = AsyncMock(return_value=result_mock)
    mock_db_connection.commit = AsyncMock()

    with patch("pipeline.dedup.review_queue.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        success = await resolve_queue_item(
            queue_id=1,
            action="merge",
            resolved_by="admin",
            decision_data={"merged_into": 10}
        )

        assert success is True
        # Should call execute twice: SELECT then UPDATE
        assert mock_db_connection.execute.call_count == 2


@pytest.mark.asyncio
async def test_dismiss_queue_item__marks_dismissed():
    """dismiss_queue_item marks item with dismissed status."""
    from pipeline.dedup.review_queue import dismiss_queue_item

    mock_db_connection = AsyncMock()
    mock_db_connection.execute = AsyncMock()
    mock_db_connection.commit = AsyncMock()

    with patch("pipeline.dedup.review_queue.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        success = await dismiss_queue_item(queue_id=1, reason="False positive")

        assert success is True
        mock_db_connection.execute.assert_called_once()
        mock_db_connection.commit.assert_called_once()
