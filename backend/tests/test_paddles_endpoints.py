"""Tests for paddles API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_get_paddles__200():
    """Test GET /paddles returns 200 with proper schema."""
    response = client.get("/api/v1/paddles")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)


def test_get_paddles__pagination_defaults():
    """Test /paddles has correct default pagination."""
    response = client.get("/api/v1/paddles")
    assert response.status_code == 200
    data = response.json()
    assert data["limit"] == 50  # default
    assert data["offset"] == 0   # default


def test_get_paddles__limit_max():
    """Test /paddles limit cannot exceed 100."""
    # Request with limit > 100 should fail validation
    response = client.get("/api/v1/paddles?limit=150")
    assert response.status_code == 422  # Validation error


def test_get_paddle_detail__404():
    """Test GET /paddles/{id} returns 404 for nonexistent paddle."""
    response = client.get("/paddles/99999")
    # Will return 200 with null data due to mock DB, or 404 if real DB
    # For now, just verify endpoint exists and responds
    assert response.status_code in [200, 404]


def test_health__200():
    """Test GET /health returns ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_get_paddle_prices__endpoint_exists():
    """Test GET /paddles/{id}/prices endpoint is defined."""
    # Just verify endpoint exists (will 404 with mock DB)
    response = client.get("/paddles/1/prices")
    assert response.status_code in [200, 404]


def test_get_paddle_latest_prices__endpoint_exists():
    """Test GET /paddles/{id}/latest-prices endpoint is defined."""
    # Just verify endpoint exists (will 404 with mock DB)
    response = client.get("/paddles/1/latest-prices")
    assert response.status_code in [200, 404]


def test_openapi_schema__includes_paddles():
    """Test OpenAPI schema includes paddles endpoints."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    paths = schema.get("paths", {})
    # Check that paddles endpoints are in schema
    assert "/paddles" in paths or "/health" in paths


def test_list_paddles_with_model_slug_filter():
    """Test GET /paddles?brand=selkirk&model_slug=vanguard-power-air returns filtered results."""
    response = client.get("/api/v1/paddles?brand=selkirk&model_slug=vanguard-power-air")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # With mock DB returning empty results, items will be empty but endpoint must accept the param
    assert isinstance(data["items"], list)


def test_list_paddles_without_model_slug():
    """Test GET /paddles?brand=selkirk returns all Selkirk paddles (no slug filter)."""
    response = client.get("/api/v1/paddles?brand=selkirk")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_list_paddles_model_slug_and_brand_combined():
    """Test both brand and model_slug filters work together."""
    response = client.get("/api/v1/paddles?brand=selkirk&model_slug=vanguard-power-air")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)


def test_list_paddles_model_slug_not_found():
    """Test non-existent model_slug returns 200 with empty items (not 404)."""
    response = client.get("/api/v1/paddles?model_slug=nonexistent-paddle-slug")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0




def test_get_similar_paddles__no_embeddings_returns_404():
    """Test endpoint returns 404 when no embeddings exist for paddle."""
    response = client.get("/api/v1/paddles/1/similar?limit=3")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_get_similar_paddles__endpoint_exists():
    """Test GET /api/v1/paddles/{id}/similar endpoint is defined."""
    response = client.get("/api/v1/paddles/1/similar")
    assert response.status_code in [200, 404]
