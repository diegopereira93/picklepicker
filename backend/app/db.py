"""Database connection pool management for FastAPI backend."""

import os
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool

_pool: AsyncConnectionPool | None = None


async def get_pool() -> AsyncConnectionPool:
    """Get or create the global async connection pool."""
    global _pool
    if _pool is None:
        _pool = AsyncConnectionPool(
            conninfo=os.environ["DATABASE_URL"],
            min_size=2,
            max_size=10,
            open=False,
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
    """Close the global connection pool gracefully."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
