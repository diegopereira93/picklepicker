import os
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool

_pool: AsyncConnectionPool | None = None


async def get_pool() -> AsyncConnectionPool:
    global _pool
    if _pool is None:
        _pool = AsyncConnectionPool(
            conninfo=os.environ["DATABASE_URL"],
            min_size=1,
            max_size=5,
        )
        await _pool.open()
    return _pool


@asynccontextmanager
async def get_connection():
    pool = await get_pool()
    async with pool.connection() as conn:
        yield conn


async def close_pool():
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
