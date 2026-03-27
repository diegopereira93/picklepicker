import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pipeline.crawlers.dropshot_brasil import (
    run_dropshot_brasil_crawler,
    save_products_to_db,
)


@pytest.mark.asyncio
async def test_happy_path__scrapes_and_saves_to_db(mock_firecrawl_app, mock_firecrawl_response, mock_db_connection):
    """Happy path: Firecrawl /extract returns products, saved to DB."""
    mock_firecrawl_app.extract.return_value = mock_firecrawl_response

    with patch("pipeline.crawlers.dropshot_brasil.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await run_dropshot_brasil_crawler(app=mock_firecrawl_app)

        # Should have called execute for each product + refresh view + commit
        assert mock_db_connection.execute.call_count >= 3  # 2 inserts + 1 view refresh
        assert result == 2  # 2 products saved


@pytest.mark.asyncio
async def test_retry_3_times__on_firecrawl_500(mock_firecrawl_app, mock_firecrawl_response):
    """Retry logic: first 2 calls fail, 3rd succeeds."""
    # Setup: first 2 calls raise, 3rd returns data
    mock_firecrawl_app.extract.side_effect = [
        Exception("Firecrawl 500"),
        Exception("Firecrawl 500"),
        mock_firecrawl_response,
    ]

    with patch("pipeline.crawlers.dropshot_brasil.get_connection") as mock_get_conn:
        mock_db = AsyncMock()
        mock_get_conn.return_value.__aenter__.return_value = mock_db

        result = await run_dropshot_brasil_crawler(app=mock_firecrawl_app)

        # Verify 3 attempts made (call_count == 3)
        assert mock_firecrawl_app.extract.call_count == 3
        assert result == 2  # Should succeed on 3rd attempt


@pytest.mark.asyncio
async def test_telegram_alert__after_3_retries_fail(mock_firecrawl_app, mock_telegram):
    """Persistent failure: 3 retries all fail → Telegram alert sent."""
    mock_firecrawl_app.extract.side_effect = Exception("Firecrawl error")

    with patch("pipeline.crawlers.dropshot_brasil.send_telegram_alert", new_callable=AsyncMock) as mock_alert:
        with pytest.raises(Exception):
            await run_dropshot_brasil_crawler(app=mock_firecrawl_app)

        # Verify Telegram alert was sent with Drop Shot Brasil in message
        mock_alert.assert_called_once()
        alert_msg = mock_alert.call_args[0][0]
        assert "Drop Shot Brasil" in alert_msg


@pytest.mark.asyncio
async def test_partial_data__missing_price_handled(mock_firecrawl_app, mock_db_connection):
    """Partial data: product missing price_brl is skipped, others saved."""
    response = {
        "data": {
            "products": [
                {
                    "name": "Selkirk Vanguard Power Air",
                    "price_brl": 1299.90,
                    "in_stock": True,
                    "image_url": "https://example.com/img.jpg",
                    "product_url": "https://example.com/1",
                    "brand": "Selkirk",
                    "specs": {},
                },
                {
                    "name": "JOOLA Ben Johns Hyperion",
                    # Missing price_brl
                    "in_stock": True,
                    "image_url": "https://example.com/img2.jpg",
                    "product_url": "https://example.com/2",
                    "brand": "JOOLA",
                    "specs": {},
                },
            ]
        }
    }
    mock_firecrawl_app.extract.return_value = response

    with patch("pipeline.crawlers.dropshot_brasil.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await run_dropshot_brasil_crawler(app=mock_firecrawl_app)

        # Only 1 product saved (the one with price)
        assert result == 1
