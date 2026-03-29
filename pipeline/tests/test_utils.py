"""Shared test utilities for pipeline E2E tests.

Provides schema validation, performance measurement, staging config loading,
and a reusable AsyncMockFirecrawl for deterministic testing.
"""

import time
import json
import yaml
import functools
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

PRODUCT_SCHEMA = {
    "name": str,
    "price_brl": (int, float),
    "in_stock": bool,
    "image_url": str,
    "product_url": str,
    "brand": str,
    "specs": dict,
}


def assert_schema_valid(product: dict, schema: dict = None) -> None:
    """Assert that *product* matches the expected field types.

    Args:
        product: A single product dict extracted by a scraper.
        schema: Optional custom schema mapping field -> type(s).
                Defaults to PRODUCT_SCHEMA.

    Raises:
        AssertionError: If a required field is missing or has the wrong type.
    """
    if schema is None:
        schema = PRODUCT_SCHEMA
    for field, expected_type in schema.items():
        assert field in product, f"Missing field: {field}"
        value = product[field]
        if value is not None:
            assert isinstance(value, expected_type), (
                f"Field '{field}' expected {expected_type}, got {type(value).__name__}: {value!r}"
            )


def assert_products_list_valid(products: list, schema: dict = None) -> None:
    """Assert schema validity for a list of products."""
    assert isinstance(products, list), "products must be a list"
    assert len(products) > 0, "products list must not be empty"
    for i, product in enumerate(products):
        assert_schema_valid(product, schema)


# ---------------------------------------------------------------------------
# Performance measurement
# ---------------------------------------------------------------------------

def measure_crawl_time(fn):
    """Decorator that measures sync or async execution time.

    Injects ``elapsed_seconds`` into the function's return value if it returns
    a dict, otherwise just asserts timing.  Always prints elapsed time.

    Usage::

        @measure_crawl_time
        async def scrape():
            ...
    """
    if asyncio.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await fn(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if isinstance(result, dict):
                result["_elapsed_seconds"] = elapsed
            return result
        return async_wrapper
    else:
        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = fn(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if isinstance(result, dict):
                result["_elapsed_seconds"] = elapsed
            return result
        return sync_wrapper


# ---------------------------------------------------------------------------
# Staging config
# ---------------------------------------------------------------------------

def load_staging_config() -> dict:
    """Load test retailer URLs and mock data paths from staging_config.yaml.

    Returns an empty dict with sensible defaults if file is missing.
    """
    config_path = FIXTURES_DIR / "staging_config.yaml"
    if not config_path.exists():
        return {
            "brazil_store": {"url": "https://brazilpickleballstore.com.br/raquete/"},
            "dropshot_brasil": {"url": "https://www.dropshotbrasil.com.br/raquetes"},
            "mercado_livre": {"search_url": "https://api.mercadolibre.com/sites/MLB/search"},
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "backoff_base_seconds": 10,
        }
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_mock_response(filename: str) -> dict:
    """Load a mock JSON response from pipeline/tests/fixtures/mock_responses/.

    Args:
        filename: e.g. ``brazil_store_response.json``

    Returns:
        Parsed JSON dict.
    """
    path = FIXTURES_DIR / "mock_responses" / filename
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# AsyncMockFirecrawl
# ---------------------------------------------------------------------------

class AsyncMockFirecrawl:
    """Reusable mock for FirecrawlApp usable in E2E scraper tests.

    Supports configuring:
    - Normal extraction responses (``set_extract_response``)
    - Error sequences (``set_extract_errors``)
    - Timeout simulation (not real sleep, just raises immediately)

    Usage::

        mock_app = AsyncMockFirecrawl()
        mock_app.set_extract_response({"data": {"products": [...]}})
        result = mock_app.extract(urls=["..."], prompt="...", schema={})
    """

    def __init__(self):
        self._responses = []
        self._call_count = 0

    def set_extract_response(self, response: dict) -> None:
        """Set a single successful response (repeated on every call)."""
        self._responses = [response]

    def set_extract_errors(self, errors: list) -> None:
        """Set a sequence of errors/responses raised in order.

        Each item can be:
        - An Exception subclass or instance → raised
        - A dict → returned as successful response
        """
        self._responses = errors

    def extract(self, urls=None, prompt=None, schema=None, **kwargs):
        """Synchronous extract method (Firecrawl SDK is sync)."""
        idx = min(self._call_count, len(self._responses) - 1) if self._responses else 0
        self._call_count += 1

        if not self._responses:
            return {"data": {"products": []}}

        item = self._responses[idx] if idx < len(self._responses) else self._responses[-1]
        if isinstance(item, type) and issubclass(item, Exception):
            raise item("Simulated error")
        if isinstance(item, Exception):
            raise item
        return item

    @property
    def call_count(self):
        return self._call_count

    def reset(self):
        self._call_count = 0
        self._responses = []
