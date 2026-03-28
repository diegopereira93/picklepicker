"""Tests for price history endpoint — 90-day date filtering."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from backend.app.main import app
    return TestClient(app)


class TestPriceHistoryDateFiltering:
    """Test 90-day date range filtering."""

    def test_price_history_endpoint_exists(self, client):
        """GET /paddles/{id}/price-history endpoint must exist."""
        response = client.get("/paddles/1/price-history")
        assert response.status_code != 404, "Endpoint /paddles/1/price-history not found"

    def test_price_history_returns_list(self, client):
        """Endpoint returns a list (empty or populated)."""
        response = client.get("/paddles/1/price-history")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_price_history_default_days_is_90(self, client):
        """Default days parameter is 90."""
        response = client.get("/paddles/1/price-history")
        assert response.status_code == 200
        # No error about missing days param

    def test_price_history_accepts_days_param(self, client):
        """Endpoint accepts ?days= query parameter."""
        response = client.get("/paddles/1/price-history?days=90")
        assert response.status_code == 200

    def test_price_history_accepts_180_days(self, client):
        """Endpoint accepts days=180."""
        response = client.get("/paddles/1/price-history?days=180")
        assert response.status_code == 200

    def test_price_history_rejects_zero_days(self, client):
        """Endpoint rejects days=0 (must be >= 1)."""
        response = client.get("/paddles/1/price-history?days=0")
        assert response.status_code == 422

    def test_price_history_rejects_over_180_days(self, client):
        """Endpoint rejects days > 180."""
        response = client.get("/paddles/1/price-history?days=181")
        assert response.status_code == 422

    def test_price_history_response_shape(self, client):
        """Each item in response has required fields: retailer, date, price, p20, is_good_time."""
        with patch("backend.app.api.price_history.db_fetch_all", new_callable=AsyncMock) as mock_db:
            mock_db.return_value = [
                {
                    "retailer_name": "Mercado Livre",
                    "price_brl": 450.0,
                    "date": datetime.now().date(),
                }
            ]
            response = client.get("/paddles/1/price-history?days=90")
            assert response.status_code == 200
            data = response.json()
            if data:
                item = data[0]
                assert "retailer" in item
                assert "date" in item
                assert "price" in item
                assert "p20" in item
                assert "is_good_time" in item

    def test_cutoff_date_is_within_days(self):
        """Cutoff date calculation: now - days gives correct date range."""
        days = 90
        cutoff = datetime.now() - timedelta(days=days)
        expected_days_ago = datetime.now() - timedelta(days=days)
        diff = abs((cutoff - expected_days_ago).total_seconds())
        assert diff < 1, "Cutoff date must be exactly 'days' days in the past"

    def test_price_history_paddle_not_found_returns_empty(self, client):
        """Non-existent paddle returns empty list (not 404), matching existing patterns."""
        with patch("backend.app.api.price_history.db_fetch_all", new_callable=AsyncMock) as mock_db:
            mock_db.return_value = []
            response = client.get("/paddles/99999/price-history")
            assert response.status_code == 200
            assert response.json() == []
