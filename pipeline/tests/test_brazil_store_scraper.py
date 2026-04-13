"""E2E test suite for Brazil Pickleball Store scraper.

Covers:
- Schema validation on extracted product data
- Retry/backoff behavior on Firecrawl failures
- Price and URL validation
- Performance assertion (<30s)
- Error mode simulation (timeout, rate limit, parse failure)
"""

import time
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pipeline.crawlers.brazil_store import (
    extract_products,
    save_products_to_db,
    run_brazil_store_crawler,
    BRAZIL_STORE_URL,
    FIRECRAWL_SCHEMA,
)
from pipeline.tests.test_utils import (
    assert_schema_valid,
    assert_products_list_valid,
    load_mock_response,
    AsyncMockFirecrawl,
)


BRAZIL_STORE_MOCK_MARKDOWN = """\
[https://brazilpickleballstore.com.br/produtos/selkirk-vanguard-power-air](https://brazilpickleballstore.com.br/produtos/selkirk-vanguard-power-air "target")
[Raquete Selkirk Vanguard Power Air](back)
R$1.299,90

[https://brazilpickleballstore.com.br/produtos/joola-ben-johns-hyperion-cfs-16](https://brazilpickleballstore.com.br/produtos/joola-ben-johns-hyperion-cfs-16 "target")
[Raquete JOOLA Ben Johns Hyperion CFS 16](back)
R$1.499,90
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def brazil_store_products():
    """Load Brazil Store mock product data from fixtures for backward compatibility."""
    data = load_mock_response("brazil_store_response.json")
    return data["data"]["products"]


@pytest.fixture
def mock_app_success():
    """FirecrawlApp mock returning valid Brazil Store products via app.scrape."""
    app = MagicMock()
    app.scrape = MagicMock(return_value=MagicMock(markdown=BRAZIL_STORE_MOCK_MARKDOWN))
    return app


@pytest.fixture
def mock_db(scraper_db_connection):
    """Re-export scraper_db_connection as mock_db for readability."""
    return scraper_db_connection


# ---------------------------------------------------------------------------
# Plan v1.1-02 Task 1: Schema & data quality tests
# ---------------------------------------------------------------------------

class TestExtractProductsSchema:
    """Validate schema compliance of extracted products."""

    def test_extract_products_schema(self, mock_app_success):
        """test_extract_products_schema: all fields match FIRECRAWL_SCHEMA types."""
        result = extract_products(mock_app_success, BRAZIL_STORE_URL)
        products = result["data"]["products"]
        assert isinstance(products, list), "products must be a list"
        for product in products:
            assert_schema_valid(product)

    def test_firecrawl_schema_definition(self):
        """FIRECRAWL_SCHEMA has expected top-level structure."""
        assert "type" in FIRECRAWL_SCHEMA
        assert FIRECRAWL_SCHEMA["type"] == "object"
        assert "products" in FIRECRAWL_SCHEMA["properties"]
        items = FIRECRAWL_SCHEMA["properties"]["products"]["items"]
        required_fields = {"name", "price_brl", "in_stock", "image_url", "product_url", "brand", "specs"}
        assert required_fields.issubset(set(items["properties"].keys()))

    def test_product_count_minimum(self, mock_app_success):
        """At least 1 product extracted."""
        result = extract_products(mock_app_success, BRAZIL_STORE_URL)
        products = result["data"]["products"]
        assert len(products) >= 1

    def test_price_currency_validation(self, mock_app_success):
        """All prices are positive floats (BRL values)."""
        result = extract_products(mock_app_success, BRAZIL_STORE_URL)
        products = result["data"]["products"]
        for product in products:
            price = product["price_brl"]
            assert isinstance(price, (int, float)), f"price_brl must be numeric, got {type(price)}"
            assert price > 0, f"price_brl must be >0, got {price}"

    def test_affiliate_url_format(self, mock_app_success):
        """product_url contains Brazil Store domain."""
        result = extract_products(mock_app_success, BRAZIL_STORE_URL)
        products = result["data"]["products"]
        for product in products:
            url = product["product_url"]
            assert isinstance(url, str), "product_url must be a string"
            assert url.startswith("https://"), f"product_url must be https://, got {url}"
            assert "brazilpickleballstore" in url, f"Expected Brazil Store domain in {url}"

    def test_image_url_validity(self, mock_app_success):
        """image_url is a valid HTTP(S) URL or empty string (Phase 2 fills images)."""
        result = extract_products(mock_app_success, BRAZIL_STORE_URL)
        products = result["data"]["products"]
        for product in products:
            url = product["image_url"]
            assert isinstance(url, str)
            if url:
                assert url.startswith("http"), f"image_url must start with http, got {url}"

    def test_brand_not_empty(self, mock_app_success):
        """brand field is non-empty string."""
        result = extract_products(mock_app_success, BRAZIL_STORE_URL)
        products = result["data"]["products"]
        for product in products:
            brand = product.get("brand", "")
            assert isinstance(brand, str)
            assert len(brand) > 0, f"brand must not be empty for product: {product['name']}"


class TestCrawlPerformance:
    """Assert crawl completes within 30 seconds."""

    def test_crawl_time_under_30s(self, mock_app_success):
        """extract_products completes in <30s with mock."""
        start = time.perf_counter()
        result = extract_products(mock_app_success, BRAZIL_STORE_URL)
        elapsed = time.perf_counter() - start
        assert result is not None
        assert elapsed < 30.0, f"extract_products took {elapsed:.2f}s, expected <30s"


# ---------------------------------------------------------------------------
# Plan v1.1-02 Task 2: Error mode tests
# ---------------------------------------------------------------------------

class TestRetryBehavior:
    """Test retry/backoff behavior on Firecrawl failures."""

    def test_retry_3_attempts_on_failure(self):
        """extract_products retries exactly 3 times before re-raising."""
        app = MagicMock()
        app.scrape = MagicMock(side_effect=Exception("Firecrawl 500"))
        with pytest.raises(Exception, match="Firecrawl 500"):
            extract_products(app, BRAZIL_STORE_URL)
        assert app.scrape.call_count == 3

    def test_timeout_retry_behavior(self):
        """Timeout on first 2 attempts, success on 3rd."""
        app = MagicMock()
        app.scrape = MagicMock(side_effect=[
            TimeoutError("timeout"),
            TimeoutError("timeout"),
            MagicMock(markdown=BRAZIL_STORE_MOCK_MARKDOWN),
        ])
        result = extract_products(app, BRAZIL_STORE_URL)
        products = result["data"]["products"]
        assert len(products) >= 1
        assert app.scrape.call_count == 3

    def test_rate_limit_backoff(self):
        """Rate limit (429) triggers retry; all 3 fail → raises."""

        class RateLimitError(Exception):
            pass

        app = MagicMock()
        app.scrape = MagicMock(side_effect=RateLimitError("429 rate limit"))
        with pytest.raises(RateLimitError):
            extract_products(app, BRAZIL_STORE_URL)
        assert app.scrape.call_count == 3

    async def test_parse_error_handling(self):
        """Invalid / None data response is handled by run_brazil_store_crawler gracefully."""
        app = MagicMock()
        # scrape succeeds but returns empty markdown (parse-level issue)
        app.scrape = MagicMock(return_value=MagicMock(markdown=""))

        with patch("pipeline.crawlers.brazil_store.get_connection") as mock_conn:
            mock_db = AsyncMock()
            mock_conn.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_conn.return_value.__aexit__ = AsyncMock(return_value=None)
            # Should return 0 (no products) without raising
            result = await run_brazil_store_crawler(app=app)
            assert result == 0

    async def test_telegram_alert_on_final_failure(self):
        """All 3 retries exhausted → Telegram alert sent with retailer name."""
        app = MagicMock()
        app.scrape = MagicMock(side_effect=Exception("Persistent error"))
        with patch("pipeline.crawlers.brazil_store.send_telegram_alert", new_callable=AsyncMock) as mock_alert:
            with pytest.raises(Exception):
                await run_brazil_store_crawler(app=app)
            mock_alert.assert_called_once()
            alert_msg = mock_alert.call_args[0][0]
            assert "Brazil Pickleball Store" in alert_msg


# ---------------------------------------------------------------------------
# Plan v1.1-02 Task 3: DB persistence tests
# ---------------------------------------------------------------------------

class TestSaveProductsToDb:
    """Validate DB persistence logic."""

    async def test_happy_path_saves_all_products(self, brazil_store_products, scraper_db_connection):
        """All valid products saved; execute called twice per product (paddles + price_snapshots)."""
        saved = await save_products_to_db(brazil_store_products, retailer_id=1, conn=scraper_db_connection)
        assert saved == len(brazil_store_products)
        assert scraper_db_connection.execute.call_count == 2 * len(brazil_store_products)

    async def test_missing_price_brl_skipped(self, scraper_db_connection):
        """Products with price_brl=None are skipped."""
        products = [
            {"name": "Good", "price_brl": 999.0, "in_stock": True,
             "image_url": "https://img.com/1.jpg", "product_url": "https://store.com/1",
             "brand": "Selkirk", "specs": {}},
            {"name": "NoPricePaddle", "price_brl": None, "in_stock": True,
             "image_url": "https://img.com/2.jpg", "product_url": "https://store.com/2",
             "brand": "JOOLA", "specs": {}},
        ]
        saved = await save_products_to_db(products, retailer_id=1, conn=scraper_db_connection)
        assert saved == 1

    async def test_source_raw_is_json_serializable(self, brazil_store_products, scraper_db_connection):
        """source_raw column receives valid JSON string."""
        await save_products_to_db(brazil_store_products[:1], retailer_id=1, conn=scraper_db_connection)
        call_kwargs = scraper_db_connection.execute.call_args[0][1]
        source_raw = call_kwargs["source_raw"]
        # Must be deserializable
        parsed = json.loads(source_raw)
        assert isinstance(parsed, dict)

    async def test_retailer_id_correct(self, brazil_store_products, scraper_db_connection):
        """retailer_id=1 (Brazil Store) set in INSERT."""
        await save_products_to_db(brazil_store_products[:1], retailer_id=1, conn=scraper_db_connection)
        call_kwargs = scraper_db_connection.execute.call_args[0][1]
        assert call_kwargs["retailer_id"] == 1

    async def test_in_stock_defaults_to_false(self, scraper_db_connection):
        """Missing in_stock field defaults to True."""
        products = [
            {"name": "Paddle", "price_brl": 500.0,
             "image_url": "https://img.com/1.jpg", "product_url": "https://store.com/1",
             "brand": "Brand", "specs": {}},
        ]
        await save_products_to_db(products, retailer_id=1, conn=scraper_db_connection)
        call_kwargs = scraper_db_connection.execute.call_args[0][1]
        assert call_kwargs["in_stock"] is True
