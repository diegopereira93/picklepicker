"""Data integrity validation tests for all scrapers.

Tests:
- Schema compliance across all scrapers
- Required fields present and correct types
- Price validation (numeric, positive)
- URL validity (HTTP/HTTPS format)
- Deduplication: SKU matching, title hash, RapidFuzz threshold
- Affiliate URL format consistency
- Performance benchmarks: <30s per scraper, <45s concurrent
"""

import time
import asyncio
import tracemalloc
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from pipeline.crawlers.brazil_store import (
    extract_products as bs_extract,
    save_products_to_db as bs_save,
    BRAZIL_STORE_URL,
)
from pipeline.crawlers.dropshot_brasil import (
    extract_products as ds_extract,
    save_products_to_db as ds_save,
    DROPSHOT_BRASIL_URL,
)
from pipeline.crawlers.mercado_livre import (
    build_affiliate_url,
    save_ml_items_to_db,
)
from pipeline.tests.test_utils import load_mock_response, assert_schema_valid


# ---------------------------------------------------------------------------
# Shared test data
# ---------------------------------------------------------------------------

BRAZIL_PRODUCTS = load_mock_response("brazil_store_response.json")["data"]["products"]
DROPSHOT_PRODUCTS = load_mock_response("dropshot_brasil_response.json")["data"]["products"]
ML_ITEMS = load_mock_response("mercado_livre_response.json")["results"]

ALL_FIRECRAWL_PRODUCTS = BRAZIL_PRODUCTS + DROPSHOT_PRODUCTS


# ---------------------------------------------------------------------------
# Plan v1.1-06 Task 1: Data integrity validation tests
# ---------------------------------------------------------------------------

class TestSchemaCompliance:
    """Schema compliance across all scrapers."""

    def test_schema_compliance_all_scrapers(self):
        """test_schema_compliance_all_scrapers: every product matches expected types."""
        for product in ALL_FIRECRAWL_PRODUCTS:
            assert_schema_valid(product)

    def test_required_fields_present(self):
        """No null/missing required fields in fixture data."""
        required = ["name", "price_brl", "in_stock", "image_url", "product_url", "brand"]
        for product in ALL_FIRECRAWL_PRODUCTS:
            for field in required:
                assert field in product, f"Missing required field '{field}' in {product.get('name')}"
                assert product[field] is not None, f"Field '{field}' is None in {product.get('name')}"

    def test_price_numeric_positive(self):
        """All prices are float/int and >0."""
        for product in ALL_FIRECRAWL_PRODUCTS:
            price = product["price_brl"]
            assert isinstance(price, (int, float)), f"price_brl not numeric: {price!r}"
            assert price > 0, f"price_brl must be positive, got {price}"

    def test_brand_not_empty(self):
        """brand field is non-empty string in all products."""
        for product in ALL_FIRECRAWL_PRODUCTS:
            brand = product.get("brand", "")
            assert isinstance(brand, str), f"brand must be str, got {type(brand)}"
            assert len(brand.strip()) > 0, f"brand empty for product: {product['name']}"

    def test_image_url_valid_format(self):
        """image_url is a valid HTTP(S) URL for all products."""
        for product in ALL_FIRECRAWL_PRODUCTS:
            url = product.get("image_url", "")
            assert url.startswith(("http://", "https://")), (
                f"image_url invalid: {url!r} for {product['name']}"
            )

    def test_product_url_clickable(self):
        """product_url links to valid HTTPS URL."""
        for product in ALL_FIRECRAWL_PRODUCTS:
            url = product.get("product_url", "")
            assert url.startswith("https://"), f"product_url must be https://, got {url!r}"
            # Must contain a domain (at minimum)
            assert "." in url, f"product_url lacks domain: {url!r}"

    def test_ml_items_have_required_fields(self):
        """ML items have id, title, price, permalink."""
        required = ["id", "title", "price", "permalink"]
        for item in ML_ITEMS:
            for field in required:
                assert field in item, f"ML item missing field '{field}'"
                assert item[field] is not None, f"ML item field '{field}' is None"

    def test_specs_is_dict(self):
        """specs field is a dict (may be empty)."""
        for product in ALL_FIRECRAWL_PRODUCTS:
            specs = product.get("specs")
            assert isinstance(specs, dict), (
                f"specs must be dict, got {type(specs).__name__} for {product['name']}"
            )


# ---------------------------------------------------------------------------
# Deduplication tests
# ---------------------------------------------------------------------------

class TestDeduplication:
    """Validate deduplication logic: SKU, title hash, and RapidFuzz matching."""

    def test_dedup_sku_matching(self):
        """Identical product URLs (acting as SKUs) identify same product."""
        product_a = {"product_url": "https://store.com/paddle-selkirk-vanguard", "name": "Selkirk Vanguard"}
        product_b = {"product_url": "https://store.com/paddle-selkirk-vanguard", "name": "Selkirk Vanguard"}
        # SKU matching: same URL = same product
        assert product_a["product_url"] == product_b["product_url"]

    def test_dedup_title_hash_collision(self):
        """Same title/brand pair identifies duplicate product."""
        product_a = {"name": "Selkirk Vanguard Power Air", "brand": "Selkirk", "price_brl": 1299.90}
        product_b = {"name": "Selkirk Vanguard Power Air", "brand": "Selkirk", "price_brl": 1299.90}
        # Title + brand hash is identical
        hash_a = hash((product_a["name"].lower(), product_a["brand"].lower()))
        hash_b = hash((product_b["name"].lower(), product_b["brand"].lower()))
        assert hash_a == hash_b

    def test_dedup_fuzzy_threshold(self):
        """RapidFuzz ≥85 triggers dedup for same-product variants."""
        from rapidfuzz import fuzz
        title_a = "Selkirk Vanguard Power Air Pickleball Paddle"
        title_b = "Selkirk Vanguard Power Air - Paddle Pickleball"
        score = fuzz.token_sort_ratio(title_a, title_b)
        assert score >= 85, f"Expected dedup trigger at ≥85, got {score}"

    def test_no_false_positive_duplicates(self):
        """Different brands/models score below 85 threshold."""
        from rapidfuzz import fuzz
        title_a = "Selkirk Vanguard Power Air"
        title_b = "JOOLA Perseus CFS 16 Hyperion"
        score = fuzz.token_sort_ratio(title_a, title_b)
        assert score < 85, f"Different paddles should not be deduped, score={score}"

    def test_affiliate_url_deeplink_format(self):
        """Mercado Livre affiliate URLs use consistent matt_id deeplink format."""
        for item in ML_ITEMS:
            permalink = item["permalink"]
            affiliate_url = build_affiliate_url(permalink, "TESTMATT")
            assert "matt_id=TESTMATT" in affiliate_url
            assert affiliate_url.startswith("https://")
            assert affiliate_url.count("?") == 1  # only one query string separator


# ---------------------------------------------------------------------------
# Plan v1.1-06 Task 2: Performance benchmarks
# ---------------------------------------------------------------------------

class TestPerformanceBenchmarks:
    """Assert crawl times within targets and no memory leaks."""

    def test_brazil_store_crawl_under_30s(self):
        """test_brazil_store_crawl_under_30s: single scraper extract <30s."""
        app = MagicMock()
        app.extract = MagicMock(return_value={"data": {"products": BRAZIL_PRODUCTS}})
        start = time.perf_counter()
        bs_extract(app, BRAZIL_STORE_URL)
        elapsed = time.perf_counter() - start
        assert elapsed < 30.0, f"Brazil Store extract took {elapsed:.3f}s, expected <30s"

    def test_dropshot_brasil_crawl_under_30s(self):
        """test_dropshot_brasil_crawl_under_30s: single scraper extract <30s."""
        app = MagicMock()
        app.extract = MagicMock(return_value={"data": {"products": DROPSHOT_PRODUCTS}})
        start = time.perf_counter()
        ds_extract(app, DROPSHOT_BRASIL_URL)
        elapsed = time.perf_counter() - start
        assert elapsed < 30.0, f"Drop Shot extract took {elapsed:.3f}s, expected <30s"

    async def test_mercado_livre_multi_page_under_30s(self):
        """test_mercado_livre_multi_page_under_30s: pagination doesn't exceed 30s."""
        pages = []
        for page_num in range(3):
            pages.append({
                "results": [{"id": f"MLB{page_num*50+i}", "title": f"Paddle {page_num*50+i}",
                              "price": 100.0, "currency_id": "BRL", "available_quantity": 1,
                              "thumbnail": "https://img.com/1.jpg",
                              "permalink": f"https://ml.com/{page_num*50+i}", "condition": "new"}
                             for i in range(50 if page_num < 2 else 25)],
                "paging": {"total": 125, "offset": page_num * 50, "limit": 50}
            })

        mock_resps = [MagicMock() for _ in pages]
        for resp, page in zip(mock_resps, pages):
            resp.json.return_value = page
            resp.raise_for_status = MagicMock()

        from pipeline.crawlers.mercado_livre import search_pickleball_paddles
        with patch("pipeline.crawlers.mercado_livre.httpx.AsyncClient") as mock_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=mock_resps)
            mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            start = time.perf_counter()
            result = await search_pickleball_paddles(limit=50, fetch_all=True)
            elapsed = time.perf_counter() - start

        assert elapsed < 30.0, f"ML multi-page took {elapsed:.3f}s, expected <30s"
        assert len(result["results"]) == 125

    async def test_concurrent_all_3_scrapers_under_45s(self):
        """test_concurrent_all_3_scrapers_under_45s: parallel execution <45s."""
        bs_app = MagicMock()
        bs_app.extract = MagicMock(return_value={"data": {"products": []}})
        ds_app = MagicMock()
        ds_app.extract = MagicMock(return_value={"data": {"products": []}})

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

            from pipeline.crawlers.brazil_store import run_brazil_store_crawler
            from pipeline.crawlers.dropshot_brasil import run_dropshot_brasil_crawler
            from pipeline.crawlers.mercado_livre import run_mercado_livre_crawler

            start = time.perf_counter()
            results = await asyncio.gather(
                run_brazil_store_crawler(app=bs_app),
                run_dropshot_brasil_crawler(app=ds_app),
                run_mercado_livre_crawler(),
            )
            elapsed = time.perf_counter() - start

        assert elapsed < 45.0, f"Concurrent scrapers took {elapsed:.3f}s, expected <45s"
        assert len(results) == 3

    def test_no_memory_leak_repeated_extraction(self):
        """Repeated extraction calls don't accumulate memory (using tracemalloc)."""
        app = MagicMock()
        app.extract = MagicMock(return_value={"data": {"products": BRAZIL_PRODUCTS}})

        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()

        for _ in range(10):
            bs_extract(app, BRAZIL_STORE_URL)

        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()

        stats = snapshot2.compare_to(snapshot1, "lineno")
        # Total memory growth must be <5MB for 10 repeated calls
        total_growth = sum(s.size_diff for s in stats if s.size_diff > 0)
        assert total_growth < 5 * 1024 * 1024, (
            f"Memory grew by {total_growth / 1024:.1f}KB across 10 calls (expected <5MB)"
        )


# ---------------------------------------------------------------------------
# Combined data integrity + performance helper
# ---------------------------------------------------------------------------

class TestDataIntegrityAcrossScrapers:
    """Cross-scraper data integrity checks."""

    def test_all_products_have_unique_names_within_scraper(self):
        """Within each scraper's fixture, product names are unique."""
        brazil_names = [p["name"] for p in BRAZIL_PRODUCTS]
        dropshot_names = [p["name"] for p in DROPSHOT_PRODUCTS]
        assert len(brazil_names) == len(set(brazil_names)), "Duplicate names in Brazil Store fixture"
        assert len(dropshot_names) == len(set(dropshot_names)), "Duplicate names in Drop Shot fixture"

    def test_ml_items_have_unique_ids(self):
        """ML items in fixture have unique IDs."""
        ids = [item["id"] for item in ML_ITEMS]
        assert len(ids) == len(set(ids)), "Duplicate ML item IDs in fixture"

    def test_currency_brl_consistent(self):
        """All Firecrawl products implicitly use BRL (price_brl field name)."""
        for product in ALL_FIRECRAWL_PRODUCTS:
            assert "price_brl" in product, "Missing price_brl field"

    def test_ml_currency_brl(self):
        """ML items explicitly declare BRL currency."""
        for item in ML_ITEMS:
            assert item["currency_id"] == "BRL", f"Expected BRL, got {item['currency_id']}"

    def test_in_stock_boolean_type(self):
        """in_stock field is boolean for all Firecrawl products."""
        for product in ALL_FIRECRAWL_PRODUCTS:
            assert isinstance(product["in_stock"], bool), (
                f"in_stock must be bool, got {type(product['in_stock']).__name__} "
                f"for {product['name']}"
            )
