import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os

# Ensure DATABASE_URL is set so pipeline.db.connection doesn't raise at import
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")


@pytest.fixture
def mock_firecrawl_app():
    app = MagicMock()
    app.extract = MagicMock()
    return app


@pytest.fixture
def mock_firecrawl_response():
    return {
        "data": {
            "products": [
                {
                    "name": "Selkirk Vanguard Power Air",
                    "price_brl": 1299.90,
                    "in_stock": True,
                    "image_url": "https://example.com/img.jpg",
                    "product_url": "https://brazilpickleballstore.com.br/product/1",
                    "brand": "Selkirk",
                    "specs": {"weight_oz": 8.4, "core_thickness_mm": 16}
                },
                {
                    "name": "JOOLA Ben Johns Hyperion",
                    "price_brl": 899.90,
                    "in_stock": True,
                    "image_url": "https://example.com/img2.jpg",
                    "product_url": "https://brazilpickleballstore.com.br/product/2",
                    "brand": "JOOLA",
                    "specs": {"weight_oz": 8.2, "core_thickness_mm": 14}
                }
            ]
        }
    }


@pytest.fixture
def mock_db_connection():
    conn = AsyncMock()
    cursor = AsyncMock()
    conn.cursor.return_value.__aenter__ = AsyncMock(return_value=cursor)
    conn.cursor.return_value.__aexit__ = AsyncMock(return_value=False)
    conn.execute = AsyncMock()
    return conn


@pytest.fixture
def mock_telegram():
    with patch("pipeline.alerts.telegram.Bot") as mock_bot_cls:
        bot_instance = AsyncMock()
        mock_bot_cls.return_value = bot_instance
        yield bot_instance


@pytest.fixture
def mock_ml_search_response():
    return {
        "results": [
            {
                "id": "MLB12345",
                "title": "Raquete Pickleball Selkirk Vanguard",
                "price": 1199.90,
                "currency_id": "BRL",
                "available_quantity": 5,
                "thumbnail": "https://http2.mlstatic.com/img1.jpg",
                "permalink": "https://www.mercadolivre.com.br/raquete-pickleball-selkirk-MLB12345",
                "condition": "new"
            },
            {
                "id": "MLB67890",
                "title": "Raquete Pickleball JOOLA Ben Johns",
                "price": 849.90,
                "currency_id": "BRL",
                "available_quantity": 3,
                "thumbnail": "https://http2.mlstatic.com/img2.jpg",
                "permalink": "https://www.mercadolivre.com.br/raquete-pickleball-joola-MLB67890",
                "condition": "new"
            }
        ],
        "paging": {"total": 120, "offset": 0, "limit": 50}
    }


@pytest.fixture
def scraper_db_connection():
    """Async DB connection mock with fetchone returning (1,) for paddle upserts."""
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
