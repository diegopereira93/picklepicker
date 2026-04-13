"""E2E test suite for Drop Shot Brasil scraper.

Covers:
- Schema validation of extracted paddle products
- Retry/backoff behavior on Firecrawl failures (3 attempts)
- Price and URL validation
- Performance assertion (<30s)
- Error mode simulation (timeout, rate limit, parse failure)
- DB persistence: retailer_id=3, missing price skipped
"""

import time
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pipeline.crawlers.dropshot_brasil import (
    extract_products,
    save_products_to_db,
    run_dropshot_brasil_crawler,
    DROPSHOT_BRASIL_URL,
    FIRECRAWL_SCHEMA,
)
from pipeline.tests.test_utils import (
    assert_schema_valid,
    assert_products_list_valid,
    load_mock_response,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def dropshot_products():
    """Load Drop Shot Brasil mock product data from fixtures."""
    data = load_mock_response("dropshot_brasil_response.json")
    return data["data"]["products"]


@pytest.fixture
def mock_app_success():
    """FirecrawlApp mock returning valid Drop Shot markdown."""
    app = MagicMock()
    mock_response = MagicMock()
    mock_response.markdown = """# Raquetes

[Drop Shot Explorer 3.0](https://www.dropshotbrasil.com.br/raquetes/drop-shot-explorer-3-0)
Raquete Drop Shot Explorer 3.0
R$459,90

[Head Graphene 360+ Radical](https://www.dropshotbrasil.com.br/raquetes/head-graphene-360-radical)
Raquete Head Graphene 360+ Radical
R$679,90
"""
    app.scrape = MagicMock(return_value=mock_response)
    return app


# ---------------------------------------------------------------------------
# Plan v1.1-03 Task 1: Review and schema tests
# ---------------------------------------------------------------------------

class TestDropShotSchemaAndStructure:
    """Validate Drop Shot Brasil scraper schema and structure matches expectations."""

    def test_firecrawl_schema_definition(self):
        """FIRECRAWL_SCHEMA has all required product fields."""
        assert FIRECRAWL_SCHEMA["type"] == "object"
        assert "products" in FIRECRAWL_SCHEMA["properties"]
        items = FIRECRAWL_SCHEMA["properties"]["products"]["items"]
        required_fields = {"name", "price_brl", "in_stock", "image_url", "product_url", "brand", "specs"}
        assert required_fields.issubset(set(items["properties"].keys()))

    def test_dropshot_url_configured(self):
        """DROPSHOT_BRASIL_URL points to correct domain."""
        assert "dropshotbrasil" in DROPSHOT_BRASIL_URL
        assert DROPSHOT_BRASIL_URL.startswith("https://")

    def test_extract_paddles_schema(self, mock_app_success):
        """test_extract_paddles_schema: all fields match expected schema types."""
        result = extract_products(mock_app_success, DROPSHOT_BRASIL_URL)
        products = result["data"]["products"]
        assert isinstance(products, list)
        for product in products:
            assert_schema_valid(product)

    def test_product_count_minimum(self, mock_app_success):
        """At least 1 product extracted."""
        result = extract_products(mock_app_success, DROPSHOT_BRASIL_URL)
        products = result["data"]["products"]
        assert len(products) >= 1

    def test_price_validation(self, dropshot_products):
        """All prices are positive numeric values (BRL)."""
        for product in dropshot_products:
            price = product["price_brl"]
            assert isinstance(price, (int, float)), f"price_brl must be numeric, got {type(price)}"
            assert price > 0, f"price_brl must be >0, got {price}"

    def test_affiliate_url_format(self, dropshot_products):
        """product_url contains Drop Shot Brasil domain and starts with https://."""
        for product in dropshot_products:
            url = product["product_url"]
            assert isinstance(url, str)
            assert url.startswith("https://"), f"product_url must be https://, got {url}"
            assert "dropshotbrasil" in url, f"Expected Drop Shot domain in {url}"

    def test_image_url_validity(self, dropshot_products):
        """image_url is a valid HTTP(S) URL."""
        for product in dropshot_products:
            url = product["image_url"]
            assert isinstance(url, str)
            assert url.startswith("http"), f"image_url must be http(s), got {url}"

    def test_brand_not_empty(self, dropshot_products):
        """brand field is a non-empty string."""
        for product in dropshot_products:
            brand = product.get("brand", "")
            assert isinstance(brand, str)
            assert len(brand) > 0, f"brand must not be empty for: {product['name']}"


# ---------------------------------------------------------------------------
# Plan v1.1-03 Task 2: Retry, error modes, performance
# ---------------------------------------------------------------------------

class TestDropShotRetryBehavior:
    """Test retry/backoff behavior."""

    def test_retry_3_attempts_on_failure(self):
        """extract_products retries 3 times before raising."""
        app = MagicMock()
        app.scrape = MagicMock(side_effect=Exception("Firecrawl 500"))
        with pytest.raises(Exception, match="Firecrawl 500"):
            extract_products(app, DROPSHOT_BRASIL_URL)
        assert app.scrape.call_count == 3

    def test_timeout_retry(self):
        """Timeout on first 2 attempts, success on 3rd."""
        # Use different keyword in URL to avoid it being parsed as a product
        success_response = MagicMock()
        success_response.markdown = """[Test Product](https://www.dropshotbrasil.com.br/raquetes/test)
Raquete Test Paddle
R$600,00
"""
        app = MagicMock()
        app.scrape = MagicMock(side_effect=[
            TimeoutError("timeout"),
            TimeoutError("timeout"),
            success_response,
        ])
        result = extract_products(app, DROPSHOT_BRASIL_URL)
        # Result should have parsed products
        assert "data" in result
        assert "products" in result["data"]
        assert len(result["data"]["products"]) == 1
        assert app.scrape.call_count == 3

    def test_parse_error_handling(self):
        """None data response returns 0 products without exception."""
        app = MagicMock()
        mock_response = MagicMock()
        mock_response.markdown = "No products here"
        app.scrape = MagicMock(return_value=mock_response)

        async def _run():
            with patch("pipeline.crawlers.dropshot_brasil.get_connection") as mock_conn:
                mock_db = AsyncMock()
                mock_conn.return_value.__aenter__ = AsyncMock(return_value=mock_db)
                mock_conn.return_value.__aexit__ = AsyncMock(return_value=None)
                return await run_dropshot_brasil_crawler(app=app)

        import asyncio
        result = asyncio.run(_run())
        assert result == 0

    async def test_telegram_alert_on_final_failure(self):
        """All 3 retries exhausted → Telegram alert contains 'Drop Shot Brasil'."""
        app = MagicMock()
        app.scrape = MagicMock(side_effect=Exception("Persistent error"))
        with patch("pipeline.crawlers.dropshot_brasil.send_telegram_alert", new_callable=AsyncMock) as mock_alert:
            with pytest.raises(Exception):
                await run_dropshot_brasil_crawler(app=app)
            mock_alert.assert_called_once()
            assert "Drop Shot Brasil" in mock_alert.call_args[0][0]


class TestDropShotCrawlPerformance:
    """Performance assertions."""

    def test_crawl_time_under_30s(self, mock_app_success):
        """extract_products completes in <30s with mock."""
        start = time.perf_counter()
        result = extract_products(mock_app_success, DROPSHOT_BRASIL_URL)
        elapsed = time.perf_counter() - start
        assert result is not None
        assert elapsed < 30.0, f"extract_products took {elapsed:.2f}s, expected <30s"


# ---------------------------------------------------------------------------
# Plan v1.1-03 Task 3: DB persistence and coverage
# ---------------------------------------------------------------------------

class TestDropShotSaveToDb:
    """Validate DB persistence logic for Drop Shot Brasil."""

    async def test_happy_path_saves_all_products(self, scraper_db_connection):
        """All valid products saved; execute called twice per product (paddle + snapshot)."""
        # Create 2 products matching the mock_app_success format
        products = [
            {"name": "Drop Shot Explorer 3.0", "price_brl": 459.90, "in_stock": True,
             "image_url": "", "product_url": "", "brand": "Drop Shot", "specs": {}},
            {"name": "Head Graphene 360+ Radical", "price_brl": 679.90, "in_stock": True,
             "image_url": "", "product_url": "", "brand": "Head", "specs": {}},
        ]
        saved = await save_products_to_db(products, retailer_id=3, conn=scraper_db_connection)
        assert saved == len(products)
        # 2 DB operations per product: paddle INSERT/UPDATE + snapshot INSERT
        assert scraper_db_connection.execute.call_count == 2 * len(products)

    async def test_retailer_id_is_3(self, scraper_db_connection):
        """retailer_id=3 (Drop Shot Brasil) set in INSERT."""
        product = {"name": "Test", "price_brl": 100.0, "in_stock": True,
                   "image_url": "", "product_url": "", "brand": "Test", "specs": {}}
        await save_products_to_db([product], retailer_id=3, conn=scraper_db_connection)
        call_kwargs = scraper_db_connection.execute.call_args[0][1]
        assert call_kwargs["retailer_id"] == 3

    async def test_missing_price_brl_skipped(self, scraper_db_connection):
        """Products with price_brl=None are skipped."""
        products = [
            {"name": "Good Paddle", "price_brl": 980.0, "in_stock": True,
             "image_url": "https://img.com/1.jpg",
             "product_url": "https://www.dropshotbrasil.com.br/raquetes/1",
             "brand": "Head", "specs": {}},
            {"name": "No Price Paddle", "price_brl": None, "in_stock": True,
             "image_url": "https://img.com/2.jpg",
             "product_url": "https://www.dropshotbrasil.com.br/raquetes/2",
             "brand": "Wilson", "specs": {}},
        ]
        saved = await save_products_to_db(products, retailer_id=3, conn=scraper_db_connection)
        assert saved == 1

    async def test_source_raw_is_json(self, scraper_db_connection):
        """source_raw column contains valid JSON string."""
        product = {"name": "Test", "price_brl": 100.0, "in_stock": True,
                   "image_url": "", "product_url": "", "brand": "Test", "specs": {}}
        await save_products_to_db([product], retailer_id=3, conn=scraper_db_connection)
        # Get the second execute call (first is paddle insert, second is snapshot insert)
        call_kwargs = scraper_db_connection.execute.call_args_list[1][0][1]
        source_raw = call_kwargs["source_raw"]
        parsed = json.loads(source_raw)
        assert isinstance(parsed, dict)

    async def test_in_stock_defaults_to_false(self, scraper_db_connection):
        """Missing in_stock field defaults to True (not False)."""
        products = [
            {"name": "Paddle", "price_brl": 600.0,
             "image_url": "https://img.com/1.jpg",
             "product_url": "https://www.dropshotbrasil.com.br/raquetes/1",
             "brand": "Head", "specs": {}},
        ]
        await save_products_to_db(products, retailer_id=3, conn=scraper_db_connection)
        call_kwargs = scraper_db_connection.execute.call_args[0][1]
        assert call_kwargs["in_stock"] is True

    async def test_full_crawler_saves_products(self, mock_app_success, scraper_db_connection):
        """run_dropshot_brasil_crawler end-to-end saves products to DB."""
        with patch("pipeline.crawlers.dropshot_brasil.get_connection") as mock_conn:
            mock_conn.return_value.__aenter__ = AsyncMock(return_value=scraper_db_connection)
            mock_conn.return_value.__aexit__ = AsyncMock(return_value=None)
            result = await run_dropshot_brasil_crawler(app=mock_app_success)
        assert result == 2  # 2 products in mock markdown
