import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from pipeline.crawlers.brazil_store import (
    extract_products,
    save_products_to_db,
    run_brazil_store_crawler,
    BRAZIL_STORE_URL,
    FIRECRAWL_SCHEMA,
)


class TestHappyPath:
    async def test_happy_path(self, mock_firecrawl_response, mock_db_connection):
        """Firecrawl returns 2 products -> both saved to price_snapshots."""
        products = mock_firecrawl_response["data"]["products"]
        retailer_id = 1  # Brazil Pickleball Store seed ID

        saved = await save_products_to_db(products, retailer_id, mock_db_connection)

        assert saved == 2
        assert mock_db_connection.execute.call_count == 4  # 2 products × 2 DB ops (paddles + price_snapshots)
        # Verify first INSERT contains correct price_brl
        first_call_args = mock_db_connection.execute.call_args_list[0]
        assert "INSERT INTO paddles" in str(first_call_args)


class TestRetryBackoff:
    async def test_retry_backoff(self, mock_firecrawl_app):
        """Firecrawl fails twice then succeeds on 3rd attempt."""
        mock_firecrawl_app.scrape = MagicMock(
            side_effect=[Exception("500 error"), Exception("500 error"), MagicMock(markdown="")]
        )
        result = extract_products(mock_firecrawl_app, "https://example.com")
        assert result == {"data": {"products": []}}
        assert mock_firecrawl_app.scrape.call_count == 3


class TestPersistentFailure:
    async def test_persistent_failure_telegram(self, mock_firecrawl_app):
        """All 3 retries fail -> Telegram alert sent."""
        mock_firecrawl_app.scrape = MagicMock(
            side_effect=Exception("500 error")
        )
        with patch("pipeline.crawlers.brazil_store.send_telegram_alert", new_callable=AsyncMock) as mock_alert:
            with pytest.raises(Exception):
                await run_brazil_store_crawler(app=mock_firecrawl_app)
            mock_alert.assert_called_once()
            alert_msg = mock_alert.call_args[0][0]
            assert "Brazil Pickleball Store" in alert_msg
            assert "3 retries" in alert_msg or "3 attempts" in alert_msg


class TestPartialData:
    async def test_partial_data(self, mock_db_connection):
        """Product with price_brl=None is skipped."""
        products = [
            {"name": "Good Paddle", "price_brl": 999.90, "in_stock": True,
             "image_url": "https://img.com/1.jpg", "product_url": "https://store.com/1",
             "brand": "Selkirk", "specs": {}},
            {"name": "Bad Paddle", "price_brl": None, "in_stock": True,
             "image_url": "https://img.com/2.jpg", "product_url": "https://store.com/2",
             "brand": "JOOLA", "specs": {}},
        ]
        saved = await save_products_to_db(products, 1, mock_db_connection)
        assert saved == 1
        assert mock_db_connection.execute.call_count == 2  # 1 valid product × 2 DB ops (paddles + price_snapshots)
