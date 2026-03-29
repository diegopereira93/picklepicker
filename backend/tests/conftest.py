"""Test configuration and fixtures."""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock psycopg_pool module before any imports that depend on it
sys.modules['psycopg_pool'] = MagicMock()

# Set a dummy DATABASE_URL for tests
os.environ.setdefault('DATABASE_URL', 'postgresql://test:test@localhost/test')


@pytest.fixture(autouse=True)
def mock_db_pool():
    """Mock database connection pool for all tests."""
    # Create mock cursor
    mock_cursor = AsyncMock()
    mock_cursor.execute = AsyncMock()
    mock_cursor.fetchone = AsyncMock(return_value={"total": 0})
    mock_cursor.fetchall = AsyncMock(return_value=[])
    mock_cursor.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor.__aexit__ = AsyncMock(return_value=None)

    # Create mock connection
    mock_conn = AsyncMock()
    mock_conn.cursor = MagicMock(return_value=mock_cursor)
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=None)

    # Create mock pool
    mock_pool = AsyncMock()
    mock_pool.connection = MagicMock(return_value=mock_conn)
    mock_pool.__aenter__ = AsyncMock(return_value=mock_pool)
    mock_pool.__aexit__ = AsyncMock(return_value=None)

    with patch('backend.app.db.get_pool', new_callable=AsyncMock) as mock_get:
        with patch('backend.app.db.close_pool', new_callable=AsyncMock) as mock_close:
            with patch('backend.app.db.get_connection') as mock_get_conn:
                mock_get.return_value = mock_pool
                mock_close.return_value = None
                mock_get_conn.return_value = mock_conn
                yield mock_pool


# ---------------------------------------------------------------------------
# Firecrawl & scraper fixtures (used by pipeline E2E tests)
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_firecrawl_app():
    """Mock FirecrawlApp instance with extract() and crawl() methods.

    Supports configuring error scenarios via side_effect.
    Scope: function (fresh mock per test).
    """
    app = MagicMock()
    app.extract = MagicMock(return_value={
        "data": {
            "products": [
                {
                    "name": "Selkirk Vanguard Power Air",
                    "price_brl": 1299.90,
                    "in_stock": True,
                    "image_url": "https://example.com/img.jpg",
                    "product_url": "https://brazilpickleballstore.com.br/product/1",
                    "brand": "Selkirk",
                    "specs": {"weight_oz": 8.4, "core_thickness_mm": 16},
                }
            ]
        }
    })
    app.crawl = MagicMock(return_value={"status": "completed", "data": []})
    return app


@pytest.fixture
def mock_firecrawl_timeout():
    """Mock FirecrawlApp that raises TimeoutError on first 2 calls, succeeds on 3rd."""
    app = MagicMock()
    app.extract = MagicMock(side_effect=[
        TimeoutError("Request timed out"),
        TimeoutError("Request timed out"),
        {
            "data": {
                "products": [
                    {
                        "name": "Test Paddle",
                        "price_brl": 500.0,
                        "in_stock": True,
                        "image_url": "https://example.com/img.jpg",
                        "product_url": "https://example.com/product/1",
                        "brand": "TestBrand",
                        "specs": {},
                    }
                ]
            }
        },
    ])
    return app


@pytest.fixture
def mock_firecrawl_rate_limit():
    """Mock FirecrawlApp that simulates 429 rate limit errors."""

    class RateLimitError(Exception):
        status_code = 429

    app = MagicMock()
    app.extract = MagicMock(side_effect=RateLimitError("Rate limit exceeded (429)"))
    return app


@pytest.fixture
def mock_firecrawl_parse_error():
    """Mock FirecrawlApp that returns unparseable / empty data."""
    app = MagicMock()
    app.extract = MagicMock(return_value={"data": None})
    return app


@pytest.fixture
def scraper_db_connection():
    """Async DB connection mock for scraper persistence tests.

    Provides execute() that returns an object with fetchone() returning (1,)
    so paddle upsert logic works correctly.
    """
    conn = AsyncMock()
    execute_result = AsyncMock()
    execute_result.fetchone = AsyncMock(return_value=(1,))
    conn.execute = AsyncMock(return_value=execute_result)
    conn.commit = AsyncMock()
    conn.__aenter__ = AsyncMock(return_value=conn)
    conn.__aexit__ = AsyncMock(return_value=None)
    return conn


@pytest.fixture
def staging_config():
    """Load staging configuration for retailer URLs and test settings."""
    from pipeline.tests.test_utils import load_staging_config
    return load_staging_config()
