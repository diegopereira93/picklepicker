"""Tests for database connection pool with asyncio.Lock."""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch, MagicMock

import pytest


class TestPoolInitialization:
    """Tests for pool initialization with asyncio.Lock."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variable for tests."""
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
        yield
        # No cleanup needed - env var is fine to keep

    @pytest.fixture(autouse=True)
    def reset_module(self):
        """Reset connection module state before each test."""
        # Remove module from cache to get fresh imports
        modules_to_remove = [k for k in sys.modules.keys() if k.startswith("pipeline.db")]
        for mod in modules_to_remove:
            del sys.modules[mod]
        yield

    async def test_pool_initializes_with_lock(self):
        """Pool should be initialized with asyncio.Lock protection."""
        with patch("pipeline.db.connection.AsyncConnectionPool") as MockPool:
            mock_pool_instance = AsyncMock()
            MockPool.return_value = mock_pool_instance

            # Import fresh module
            from pipeline.db.connection import get_pool, _pool, _pool_lock

            # Verify lock is None initially
            assert _pool_lock is None

            # First call should create pool
            pool = await get_pool()

            # Verify lock was created
            from pipeline.db.connection import _pool_lock as updated_lock
            assert updated_lock is not None
            assert isinstance(updated_lock, asyncio.Lock)

    async def test_concurrent_calls_return_same_pool(self):
        """Multiple concurrent calls should return the same pool instance."""
        with patch("pipeline.db.connection.AsyncConnectionPool") as MockPool:
            mock_pool_instance = AsyncMock()
            MockPool.return_value = mock_pool_instance

            # Import fresh
            from pipeline.db.connection import get_pool

            # Launch multiple concurrent get_pool calls
            results = await asyncio.gather(
                get_pool(),
                get_pool(),
                get_pool(),
            )

            # All should return the same pool instance
            assert results[0] is results[1]
            assert results[1] is results[2]

            # Pool should only be created once
            MockPool.assert_called_once()

    async def test_double_checked_locking_pattern(self):
        """Double-checked locking should prevent duplicate initialization."""
        call_count = 0

        def slow_init(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock = AsyncMock()
            return mock

        with patch("pipeline.db.connection.AsyncConnectionPool") as MockPool:
            MockPool.side_effect = slow_init

            from pipeline.db.connection import get_pool

            # Launch concurrent calls
            results = await asyncio.gather(
                get_pool(),
                get_pool(),
                get_pool(),
            )

            # Should only initialize once despite concurrent access
            assert call_count == 1
            assert results[0] is results[1] is results[2]

    async def test_subsequent_calls_return_cached_pool(self):
        """Subsequent calls should return cached pool without re-acquiring lock."""
        with patch("pipeline.db.connection.AsyncConnectionPool") as MockPool:
            mock_pool_instance = AsyncMock()
            MockPool.return_value = mock_pool_instance

            from pipeline.db.connection import get_pool

            # First call creates pool
            pool1 = await get_pool()

            # Reset mock to verify no new pool created
            MockPool.reset_mock()

            # Second call should return cached pool
            pool2 = await get_pool()
            pool3 = await get_pool()

            assert pool1 is pool2 is pool3
            MockPool.assert_not_called()

    async def test_close_pool_resets_lock(self):
        """close_pool should reset both pool and lock."""
        with patch("pipeline.db.connection.AsyncConnectionPool") as MockPool:
            mock_pool_instance = AsyncMock()
            MockPool.return_value = mock_pool_instance

            from pipeline.db.connection import get_pool, close_pool, _pool, _pool_lock

            # Initialize pool
            await get_pool()

            import pipeline.db.connection as conn_module
            assert conn_module._pool is not None
            assert conn_module._pool_lock is not None

            # Close pool
            await close_pool()

            # Both should be reset
            assert conn_module._pool is None
            assert conn_module._pool_lock is None

    async def test_close_pool_when_already_closed(self):
        """close_pool should handle already-closed state gracefully."""
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"

        with patch("pipeline.db.connection.AsyncConnectionPool"):
            from pipeline.db.connection import close_pool, _pool, _pool_lock

            import pipeline.db.connection as conn_module

            # Ensure pool is None
            conn_module._pool = None
            conn_module._pool_lock = None

            # Should not raise
            await close_pool()

            assert conn_module._pool is None


class TestPoolTypeHints:
    """Tests for type hints and API surface."""

    async def test_get_pool_returns_async_pool(self):
        """get_pool should return AsyncConnectionPool type."""
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"

        with patch("pipeline.db.connection.AsyncConnectionPool") as MockPool:
            mock_pool_instance = AsyncMock()
            MockPool.return_value = mock_pool_instance

            from pipeline.db.connection import get_pool

            pool = await get_pool()
            assert pool is not None


class TestTransactionRollback:
    """Tests for transaction rollback on exception."""

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variable for tests."""
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
        yield

    @pytest.fixture(autouse=True)
    def reset_module(self):
        """Reset connection module state before each test."""
        modules_to_remove = [k for k in sys.modules.keys() if k.startswith("pipeline.db")]
        for mod in modules_to_remove:
            del sys.modules[mod]
        yield

    def _create_mock_pool(self):
        """Helper to create properly mocked pool and connection."""
        mock_conn = AsyncMock()
        mock_pool = AsyncMock()
        # Create async context manager for pool.connection()
        mock_cm = AsyncMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_cm.__aexit__ = AsyncMock(return_value=None)
        mock_pool.connection = MagicMock(return_value=mock_cm)
        return mock_pool, mock_conn

    async def test_transaction_rollback_on_exception(self):
        """Exception in get_connection context triggers automatic rollback."""
        mock_pool, mock_conn = self._create_mock_pool()

        with patch("pipeline.db.connection.get_pool", return_value=mock_pool):
            from pipeline.db.connection import get_connection

            with pytest.raises(ValueError, match="Simulated error"):
                async with get_connection() as conn:
                    raise ValueError("Simulated error")

            # Verify rollback was called
            mock_conn.rollback.assert_called_once()

    async def test_connection_returned_to_pool_after_rollback(self):
        """Connection returned to pool in clean state after rollback."""
        mock_pool, mock_conn = self._create_mock_pool()

        with patch("pipeline.db.connection.get_pool", return_value=mock_pool):
            from pipeline.db.connection import get_connection

            try:
                async with get_connection() as conn:
                    raise ValueError("Simulated error")
            except ValueError:
                pass

            # Verify rollback was called before connection exit
            mock_conn.rollback.assert_called_once()

    async def test_original_exception_re_raised_after_rollback(self):
        """Original exception re-raised after rollback."""
        mock_pool, mock_conn = self._create_mock_pool()

        with patch("pipeline.db.connection.get_pool", return_value=mock_pool):
            from pipeline.db.connection import get_connection

            with pytest.raises(RuntimeError, match="Custom error"):
                async with get_connection() as conn:
                    raise RuntimeError("Custom error")

            # Verify rollback was still called
            mock_conn.rollback.assert_called_once()

    async def test_no_rollback_on_success(self):
        """No rollback called when no exception."""
        mock_pool, mock_conn = self._create_mock_pool()

        with patch("pipeline.db.connection.get_pool", return_value=mock_pool):
            from pipeline.db.connection import get_connection

            async with get_connection() as conn:
                # Normal operation, no exception
                pass

            # Verify rollback was NOT called
            mock_conn.rollback.assert_not_called()
