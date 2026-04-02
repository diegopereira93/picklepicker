import asyncio
import logging
import os
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)

_pool: AsyncConnectionPool | None = None
_pool_lock: asyncio.Lock | None = None


async def get_pool() -> AsyncConnectionPool:
    """Get or create the async connection pool with thread-safe initialization.

    Uses double-checked locking pattern to ensure pool is created exactly once
    even when called concurrently from multiple async tasks.

    Connection pool configuration:
    - max_waiting=10: Queue up to 10 waiting connections (backpressure)
    - max_idle=300: Close idle connections after 5 minutes
    - max_lifetime=3600: Recycle connections after 1 hour
    """
    global _pool, _pool_lock
    if _pool_lock is None:
        _pool_lock = asyncio.Lock()
    if _pool is None:
        async with _pool_lock:
            if _pool is None:  # Double-check after acquiring lock
                _pool = AsyncConnectionPool(
                    conninfo=os.environ["DATABASE_URL"],
                    min_size=1,
                    max_size=5,
                    max_waiting=10,  # Queue up to 10 waiting connections
                    max_idle=300,    # Close idle connections after 5 minutes
                    max_lifetime=3600,  # Recycle connections after 1 hour
                )
                await _pool.open()
    return _pool


@asynccontextmanager
async def get_connection():
    """Get a connection from the pool as an async context manager.

    Automatically rolls back on exception to prevent pool poisoning from
    uncommitted transactions. The original exception is re-raised after
    rollback so callers can handle it appropriately.
    """
    pool = await get_pool()
    async with pool.connection() as conn:
        try:
            yield conn
        except Exception:
            # Rollback on any exception to prevent pool poisoning
            try:
                await conn.rollback()
                logger.debug("Transaction rolled back due to exception")
            except Exception as rollback_err:
                logger.warning(f"Rollback failed: {rollback_err}")
            raise  # Re-raise original exception


async def close_pool():
    """Close the connection pool and reset state."""
    global _pool, _pool_lock
    if _pool is not None:
        await _pool.close()
        _pool = None
        _pool_lock = None
