"""Tests for price alerts API endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_price_alerts_db():
    """Mock DB specifically for price alerts tests."""
    mock_cursor = AsyncMock()
    mock_conn = AsyncMock()
    mock_pool = AsyncMock()

    _duplicate_exists = {"exists": False}
    _fetchone_call_count = {"count": 0}

    def fetchone_side_effect():
        _fetchone_call_count["count"] += 1
        if _duplicate_exists["exists"]:
            return {"id": 1}
        if _fetchone_call_count["count"] == 1:
            return None
        return {
            "id": 1,
            "user_id": 1,
            "paddle_id": 1,
            "target_price_brl": 500.0,
            "is_active": True,
            "created_at": "2026-04-12T00:00:00Z"
        }

    mock_cursor.fetchone.side_effect = fetchone_side_effect
    mock_cursor.fetchall = AsyncMock(return_value=[])
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=None)

    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)

    mock_pool.connection = MagicMock(return_value=mock_conn)
    mock_pool.__aenter__ = AsyncMock(return_value=mock_pool)
    mock_pool.__aexit__ = AsyncMock(return_value=None)

    def set_duplicate_exists(exists):
        _duplicate_exists["exists"] = exists
        _fetchone_call_count["count"] = 0

    with patch('app.db.get_pool', return_value=mock_pool):
        with patch('app.db.close_pool', return_value=None):
            with patch('app.db.get_connection', return_value=mock_conn):
                yield set_duplicate_exists


def test_create_price_alert__201(mock_price_alerts_db):
    """Test POST /price-alerts creates alert and returns 201."""
    mock_price_alerts_db(False)

    payload = {
        "user_id": 1,
        "paddle_id": 1,
        "target_price_brl": 500.0
    }
    response = client.post("/api/v1/price-alerts", json=payload)
    assert response.status_code == 201


def test_create_price_alert__missing_fields__422():
    """Test POST /price-alerts returns 422 for missing required fields."""
    payload = {
        "user_id": 1
    }
    response = client.post("/api/v1/price-alerts", json=payload)
    assert response.status_code == 422


def test_create_price_alert__duplicate__409(mock_price_alerts_db):
    """Test POST /price-alerts returns 409 for duplicate alert (same user_id + paddle_id)."""
    mock_price_alerts_db(True)

    payload = {
        "user_id": 1,
        "paddle_id": 1,
        "target_price_brl": 500.0
    }
    response = client.post("/api/v1/price-alerts", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"].lower()


def test_list_price_alerts__200():
    """Test GET /price-alerts?user_id=X returns user's alerts."""
    user_id = 1
    response = client.get(f"/api/v1/price-alerts?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_price_alerts__missing_user_id__422():
    """Test GET /price-alerts returns 422 for missing user_id query param."""
    response = client.get("/api/v1/price-alerts")
    assert response.status_code == 422
