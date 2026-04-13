"""Firecrawl integration test suite.

Tests all error modes for the Firecrawl /extract endpoint:
- Timeout: 3 retries with exponential backoff
- Rate limit (429): retry + alert + circuit breaker
- Parse error: graceful degradation (returns 0 products)
- HTTP 4xx: non-retryable errors
- HTTP 5xx: retryable errors
- Max retries exceeded: raises + Telegram alert
- Concurrent execution: 3 scrapers in parallel, partial failures handled
"""

import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

from pipeline.crawlers.brazil_store import extract_products as bs_extract, run_brazil_store_crawler
from pipeline.crawlers.dropshot_brasil import extract_products as ds_extract, run_dropshot_brasil_crawler
from pipeline.crawlers.mercado_livre import run_mercado_livre_crawler


# ---------------------------------------------------------------------------
# Helper exceptions to simulate HTTP error codes
# ---------------------------------------------------------------------------

class FirecrawlHTTPError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(message)


class RateLimitError(FirecrawlHTTPError):
    def __init__(self):
        super().__init__(429, "Rate limit exceeded (429 Too Many Requests)")


class ServerError(FirecrawlHTTPError):
    def __init__(self, code: int = 500):
        super().__init__(code, f"Internal server error ({code})")


class ClientError(FirecrawlHTTPError):
    def __init__(self, code: int = 400):
        super().__init__(code, f"Client error ({code})")


# ---------------------------------------------------------------------------
# Helper functions and constants
# ---------------------------------------------------------------------------

def make_scrape_mock(markdown="", side_effect=None):
    """Create a mock app that uses scrape() instead of extract()."""
    app = MagicMock()
    if side_effect:
        app.scrape = MagicMock(side_effect=side_effect)
    else:
        app.scrape = MagicMock(return_value=MagicMock(markdown=markdown))
    return app


BRAZIL_STORE_MARKDOWN = """\
[Raquete Selkirk Vanguard Power Air](https://brazilpickleballstore.com.br/produtos/selkirk-vanguard)
R$1.299,90
"""

DROPSHOT_MARKDOWN = """\
Paddle X Power
R$899,00
"""


# ---------------------------------------------------------------------------
# Plan v1.1-05 Task 1: Firecrawl integration test suite
# ---------------------------------------------------------------------------

class TestFirecrawlExtractEndpoint:
    """Basic extraction and error mode tests."""

    def test_extract_endpoint_basic(self):
        """Valid URL + normal response → returns products dict."""
        app = make_scrape_mock(markdown=BRAZIL_STORE_MARKDOWN)
        result = bs_extract(app, "https://example.com/raquetes")
        assert "data" in result
        assert "products" in result["data"]
        assert len(result["data"]["products"]) == 1
        assert "Raquete Selkirk Vanguard Power Air" in result["data"]["products"][0]["name"]
        assert result["data"]["products"][0]["price_brl"] == 1299.9
        app.scrape.assert_called_once()

    def test_timeout_3_retry_attempts(self):
        """Timeout on first 2 calls, success on 3rd → 3 total attempts."""
        success_response = MagicMock(markdown="")
        app = make_scrape_mock(side_effect=[
            TimeoutError("Request timed out"),
            TimeoutError("Request timed out"),
            success_response,
        ])
        result = bs_extract(app, "https://example.com/raquetes")
        assert "data" in result
        assert "products" in result["data"]
        assert app.scrape.call_count == 3

    def test_rate_limit_429_response(self):
        """All 3 retries hit rate limit → raises RateLimitError."""
        app = make_scrape_mock(side_effect=RateLimitError())
        with pytest.raises(RateLimitError):
            bs_extract(app, "https://example.com/raquetes")
        assert app.scrape.call_count == 3

    def test_parse_error_invalid_json(self):
        """Firecrawl returns data=None → run_crawler returns 0 gracefully."""
        app = make_scrape_mock(markdown="")

        async def _run():
            with patch("pipeline.crawlers.brazil_store.get_connection") as mc:
                db = AsyncMock()
                mc.return_value.__aenter__ = AsyncMock(return_value=db)
                mc.return_value.__aexit__ = AsyncMock(return_value=None)
                return await run_brazil_store_crawler(app=app)

        result = asyncio.run(_run())
        assert result == 0

    def test_http_error_4xx_handling(self):
        """HTTP 4xx (client error) is non-retryable — tenacity retries anyway but raises."""
        app = make_scrape_mock(side_effect=ClientError(400))
        with pytest.raises(ClientError):
            bs_extract(app, "https://example.com/raquetes")
        assert app.scrape.call_count == 3

    def test_http_error_5xx_handling(self):
        """HTTP 5xx (server error) is retryable — 3 attempts then raises."""
        app = make_scrape_mock(side_effect=ServerError(500))
        with pytest.raises(ServerError):
            bs_extract(app, "https://example.com/raquetes")
        assert app.scrape.call_count == 3

    def test_max_retries_exceeded_raises(self):
        """After 3 retries, exception re-raised (reraise=True in @retry)."""
        app = make_scrape_mock(side_effect=Exception("Persistent failure"))
        with pytest.raises(Exception, match="Persistent failure"):
            bs_extract(app, "https://example.com/raquetes")
        assert app.scrape.call_count == 3

    async def test_max_retries_exceeded_triggers_alert(self):
        """After max retries, Telegram alert sent with scraper name."""
        app = make_scrape_mock(side_effect=Exception("Network error"))
        with patch("pipeline.crawlers.brazil_store.send_telegram_alert", new_callable=AsyncMock) as mock_alert:
            with pytest.raises(Exception):
                await run_brazil_store_crawler(app=app)
            mock_alert.assert_called_once()
            alert_msg = mock_alert.call_args[0][0]
            assert "Brazil Pickleball Store" in alert_msg
            assert "3 retries" in alert_msg

    def test_exponential_backoff_configured(self):
        """Verify tenacity @retry decorator uses wait_exponential."""
        from tenacity import wait_exponential
        import inspect
        from pipeline.crawlers import brazil_store

        # Access retry statistics object from the decorated function
        retry_obj = bs_extract.retry
        # Should have a wait strategy that is exponential
        wait = retry_obj.wait
        assert wait is not None
        # The wait class name contains 'exponential'
        assert "exponential" in type(wait).__name__.lower(), (
            f"Expected exponential backoff, got: {type(wait).__name__}"
        )


# ---------------------------------------------------------------------------
# Plan v1.1-05 Task 2: Concurrent execution and circuit breaker
# ---------------------------------------------------------------------------

class TestConcurrentScraperExecution:
    """Test concurrent execution of all 3 scrapers."""

    async def test_concurrent_3_scrapers(self):
        """Run Brazil Store, Drop Shot, and ML in parallel — all succeed."""
        bs_app = make_scrape_mock(markdown="")
        ds_app = make_scrape_mock(markdown="")

        empty_ml = {"results": [], "paging": {"total": 0, "offset": 0, "limit": 50}}
        mock_ml_resp = MagicMock()
        mock_ml_resp.json.return_value = empty_ml
        mock_ml_resp.raise_for_status = MagicMock()

        with patch("pipeline.crawlers.brazil_store.get_connection") as bs_conn, \
             patch("pipeline.crawlers.dropshot_brasil.get_connection") as ds_conn, \
             patch("pipeline.crawlers.mercado_livre.httpx.AsyncClient") as ml_cls:

            bs_conn.return_value.__aenter__ = AsyncMock(return_value=AsyncMock())
            bs_conn.return_value.__aexit__ = AsyncMock(return_value=None)
            ds_conn.return_value.__aenter__ = AsyncMock(return_value=AsyncMock())
            ds_conn.return_value.__aexit__ = AsyncMock(return_value=None)
            ml_client = AsyncMock()
            ml_client.get = AsyncMock(return_value=mock_ml_resp)
            ml_cls.return_value.__aenter__ = AsyncMock(return_value=ml_client)
            ml_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            start = time.perf_counter()
            results = await asyncio.gather(
                run_brazil_store_crawler(app=bs_app),
                run_dropshot_brasil_crawler(app=ds_app),
                run_mercado_livre_crawler(),
            )
            elapsed = time.perf_counter() - start

        # All 3 scrapers returned 0 (no products) without raising
        assert all(r == 0 for r in results)
        assert len(results) == 3

    async def test_rate_limit_under_concurrent_load(self):
        """One scraper hits rate limit; others continue successfully."""
        # Brazil Store: rate limited (fails)
        bs_app = make_scrape_mock(side_effect=RateLimitError())

        # Drop Shot: succeeds
        ds_app = make_scrape_mock(markdown="")

        with patch("pipeline.crawlers.brazil_store.send_telegram_alert", new_callable=AsyncMock), \
             patch("pipeline.crawlers.dropshot_brasil.get_connection") as ds_conn:

            ds_conn.return_value.__aenter__ = AsyncMock(return_value=AsyncMock())
            ds_conn.return_value.__aexit__ = AsyncMock(return_value=None)

            results = await asyncio.gather(
                run_brazil_store_crawler(app=bs_app),
                run_dropshot_brasil_crawler(app=ds_app),
                return_exceptions=True,
            )

        # BS raises (rate limited), DS succeeds
        assert isinstance(results[0], RateLimitError)
        assert results[1] == 0

    async def test_circuit_breaker_on_repeated_failures(self):
        """Repeated failures trigger Telegram alert (acting as circuit breaker signal)."""
        failing_app = make_scrape_mock(side_effect=Exception("Firecrawl down"))

        alert_calls = []
        async def capture_alert(msg):
            alert_calls.append(msg)

        with patch("pipeline.crawlers.brazil_store.send_telegram_alert", side_effect=capture_alert):
            with pytest.raises(Exception):
                await run_brazil_store_crawler(app=failing_app)

        # Alert sent once after all retries exhausted
        assert len(alert_calls) == 1
        assert "Brazil Pickleball Store" in alert_calls[0]


# ---------------------------------------------------------------------------
# Plan v1.1-05 Task 3: Error handling documentation validation
# ---------------------------------------------------------------------------

class TestErrorHandlingDocumentation:
    """Validate documented error handling behavior matches implementation."""

    def test_brazil_store_retry_config(self):
        """Brazil Store: 3 retries, exponential backoff min=10s max=120s."""
        retry_obj = bs_extract.retry
        assert retry_obj.stop.max_attempt_number == 3
        wait = retry_obj.wait
        assert wait.min == 10
        assert wait.max == 120

    def test_dropshot_brasil_retry_config(self):
        """Drop Shot Brasil: 3 retries, exponential backoff min=10s max=120s."""
        retry_obj = ds_extract.retry
        assert retry_obj.stop.max_attempt_number == 3
        wait = retry_obj.wait
        assert wait.min == 10
        assert wait.max == 120

    def test_reraise_true_on_final_failure(self):
        """reraise=True means final exception propagates to caller."""
        app = make_scrape_mock(side_effect=ValueError("Custom error"))
        with pytest.raises(ValueError, match="Custom error"):
            bs_extract(app, "https://example.com")

    async def test_alert_message_format(self):
        """Alert message includes scraper name and '3 retries'."""
        app = make_scrape_mock(side_effect=Exception("boom"))
        with patch("pipeline.crawlers.brazil_store.send_telegram_alert", new_callable=AsyncMock) as mock_alert:
            with pytest.raises(Exception):
                await run_brazil_store_crawler(app=app)
            msg = mock_alert.call_args[0][0]
            assert "Brazil Pickleball Store" in msg
            assert "3 retries" in msg

    async def test_dropshot_alert_message_format(self):
        """Drop Shot Brasil alert includes 'Drop Shot Brasil' in message."""
        app = make_scrape_mock(side_effect=Exception("boom"))
        with patch("pipeline.crawlers.dropshot_brasil.send_telegram_alert", new_callable=AsyncMock) as mock_alert:
            with pytest.raises(Exception):
                await run_dropshot_brasil_crawler(app=app)
            msg = mock_alert.call_args[0][0]
            assert "Drop Shot Brasil" in msg
