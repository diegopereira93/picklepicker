"""Tests for affiliate click tracking endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, follow_redirects=False)


@pytest.fixture
def mock_affiliate_db():
    """Override autouse mock with affiliate-aware cursor."""
    mock_cursor = AsyncMock()
    mock_cursor.execute = AsyncMock()
    mock_cursor.fetchone = AsyncMock(
        return_value={"id": 1, "paddle_id": 1, "retailer": None, "created_at": "2026-04-12T00:00:00"}
    )
    mock_cursor.fetchall = AsyncMock(return_value=[])
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=None)

    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)

    mock_pool = AsyncMock()
    mock_pool.connection = MagicMock(return_value=mock_conn)
    mock_pool.__aenter__ = AsyncMock(return_value=mock_pool)
    mock_pool.__aexit__ = AsyncMock(return_value=None)

    with patch('app.db.get_pool', return_value=mock_pool):
        with patch('app.db.close_pool', return_value=None):
            with patch('app.db.get_connection', return_value=mock_conn):
                yield mock_cursor


def test_post_affiliate_click__201(mock_affiliate_db):
    payload = {
        "paddle_id": 1,
        "retailer": "brazilpickleballstore",
        "source": "organic",
        "campaign": "search",
        "medium": "affiliate",
        "page": "https://pickleiq.com/chat",
        "affiliate_url": "https://brazilpickleballstore.com.br/product/1"
    }
    response = client.post("/api/v1/affiliate-clicks", json=payload)
    assert response.status_code == 201


def test_post_affiliate_click__minimal_payload(mock_affiliate_db):
    payload = {
        "paddle_id": 1,
        "affiliate_url": "https://example.com/product/1"
    }
    response = client.post("/api/v1/affiliate-clicks", json=payload)
    assert response.status_code == 201


def test_post_affiliate_click__optional_fields_null(mock_affiliate_db):
    payload = {
        "retailer": "testretailer",
        "affiliate_url": "https://example.com/product/1"
    }
    response = client.post("/api/v1/affiliate-clicks", json=payload)
    assert response.status_code == 201


def test_get_track_affiliate__redirect_with_url(mock_affiliate_db):
    params = {
        "utm_source": "test_source",
        "utm_campaign": "test_campaign",
        "utm_medium": "test_medium",
        "paddle_id": 1,
        "redirect_url": "https://example.com/product/1"
    }
    response = client.get("/api/track-affiliate", params=params)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/product/1"


def test_get_track_affiliate__encoded_url(mock_affiliate_db):
    encoded_url = "https%3A%2F%2Fexample.com%2Fproduct%2F1%3Fparam%3Dvalue"
    params = {
        "redirect_url": encoded_url,
        "paddle_id": 1
    }
    response = client.get("/api/track-affiliate", params=params)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/product/1?param=value"


def test_get_track_affiliate__missing_redirect_url(mock_affiliate_db):
    params = {
        "paddle_id": 1
    }
    response = client.get("/api/track-affiliate", params=params)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Missing redirect_url" in data["detail"]


def test_get_track_affiliate__defaults(mock_affiliate_db):
    params = {
        "redirect_url": "https://example.com/product/1",
        "paddle_id": 1
    }
    response = client.get("/api/track-affiliate", params=params)
    assert response.status_code == 302


def test_get_track_affiliate__invalid_paddle_id(mock_affiliate_db):
    params = {
        "redirect_url": "https://example.com/product/1",
        "paddle_id": -999
    }
    response = client.get("/api/track-affiliate", params=params)
    assert response.status_code == 302


def test_post_affiliate_click__validation_error():
    payload = {
        "paddle_id": "not_a_number",
        "affiliate_url": "https://example.com"
    }
    response = client.post("/api/v1/affiliate-clicks", json=payload)
    assert response.status_code == 422


def test_openapi_schema__includes_affiliate_endpoints():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})
    assert "/api/v1/affiliate-clicks" in paths
    assert "/api/track-affiliate" in paths
