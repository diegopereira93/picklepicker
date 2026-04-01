import asyncio
import os
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool

_pool: AsyncConnectionPool | None = None
_pool_lock: asyncio.Lock | None = None


async def get_pool() -> AsyncConnectionPool:
    """Get or create the async connection pool with thread-safe initialization.

    Uses double-checked locking pattern to ensure pool is created exactly once
    even when called concurrently from multiple async tasks.
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
                )
                await _pool.open()
    return _pool


@asynccontextmanager
async def get_connection():
    """Get a connection from the pool as an async context manager."""
    pool = await get_pool()
    async with pool.connection() as conn:
        yield conn


async def close_pool():
    """Close the connection pool and reset state."""
    global _pool, _pool_lock
    if _pool is not None:
        await _pool.close()
        _pool = None
        _pool_lock = None
