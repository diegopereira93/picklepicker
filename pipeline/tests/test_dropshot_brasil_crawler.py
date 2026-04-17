import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pipeline.crawlers.dropshot_brasil import (
    run_dropshot_brasil_crawler,
    save_products_to_db,
)


@pytest.mark.asyncio
async def test_happy_path__scrapes_and_saves_to_db(mock_firecrawl_app, mock_db_connection):
    """Happy path: Firecrawl scrape returns markdown with products, saved to DB."""
    # Mock app.scrape to return parseable markdown with Dropshot-style products
    mock_response = MagicMock()
    mock_response.markdown = """# Raquetes

[Drop Shot Explorer 3.0](https://www.dropshotbrasil.com.br/raquetes/drop-shot-explorer-3-0)
Raquete Drop Shot Explorer 3.0
R$459,90

[Head Graphene 360+ Radical](https://www.dropshotbrasil.com.br/raquetes/head-graphene-360-radical)
Raquete Head Graphene 360+ Radical
R$679,90
"""
    mock_firecrawl_app.scrape.return_value = mock_response

    with patch("pipeline.crawlers.dropshot_brasil.get_connection") as mock_get_conn:
        # Mock fetchone to return paddle IDs
        execute_result = AsyncMock()
        execute_result.fetchone = AsyncMock(return_value=(1,))
        mock_db_connection.execute = AsyncMock(return_value=execute_result)
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await run_dropshot_brasil_crawler(app=mock_firecrawl_app)

        # Should have called execute for each product (2 DB ops each) + refresh view
        # 2 products × 2 DB operations (paddle INSERT + snapshot INSERT) + 1 view refresh = 5
        assert mock_db_connection.execute.call_count == 5
        assert result == 2  # 2 products saved


@pytest.mark.asyncio
async def test_retry_3_times__on_firecrawl_500(mock_firecrawl_app, mock_db_connection):
    """Retry logic: first 2 calls fail, 3rd succeeds."""
    # Setup: first 2 calls raise, 3rd returns markdown with products
    mock_response = MagicMock()
    mock_response.markdown = """# Raquetes

[Test Product](https://www.dropshotbrasil.com.br/raquetes/test)
Raquete Test Paddle
R$600,00
"""

    mock_firecrawl_app.scrape.side_effect = [
        Exception("Firecrawl 500"),
        Exception("Firecrawl 500"),
        mock_response,
    ]

    with patch("pipeline.crawlers.dropshot_brasil.get_connection") as mock_get_conn:
        execute_result = AsyncMock()
        execute_result.fetchone = AsyncMock(return_value=(1,))
        mock_db_connection.execute = AsyncMock(return_value=execute_result)
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await run_dropshot_brasil_crawler(app=mock_firecrawl_app)

        # Verify 3 attempts made for extract_products + 1 for Phase 2 product page scrape = 4 total
        assert mock_firecrawl_app.scrape.call_count == 4
        assert result == 1  # Should succeed on 3rd attempt (1 product)


@pytest.mark.asyncio
async def test_telegram_alert__after_3_retries_fail(mock_firecrawl_app):
    """Persistent failure: 3 retries all fail → Telegram alert sent."""
    mock_firecrawl_app.scrape.side_effect = Exception("Firecrawl error")

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
    # Mock markdown: first product has price, second doesn't (price not found in markdown)
    mock_response = MagicMock()
    mock_response.markdown = """# Raquetes

[Selkirk Vanguard Power Air](https://example.com/1)
Raquete Selkirk Vanguard Power Air
R$1299,90

[JOOLA Ben Johns Hyperion](https://example.com/2)
Raquete JOOLA Ben Johns Hyperion
No price here
"""
    mock_firecrawl_app.scrape.return_value = mock_response

    with patch("pipeline.crawlers.dropshot_brasil.get_connection") as mock_get_conn:
        execute_result = AsyncMock()
        execute_result.fetchone = AsyncMock(return_value=(1,))
        mock_db_connection.execute = AsyncMock(return_value=execute_result)
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await run_dropshot_brasil_crawler(app=mock_firecrawl_app)

        # Only 1 product saved (the one with price)
        assert result == 1
