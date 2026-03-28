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
