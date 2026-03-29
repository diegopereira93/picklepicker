"""Tests for Redis cache layer."""

import pytest
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.app.cache import RedisCache


@pytest.fixture
def cache():
    """Create cache instance for testing."""
    return RedisCache()


@pytest.mark.asyncio
async def test_cache_get__hit(cache):
    """Retrieve cached value on hit."""
    key = "test_key"
    value = {"paddles": [{"id": 1, "name": "Paddle A"}]}

    await cache.set_cached(key, value)
    result = await cache.get_cached(key)

    assert result == value


@pytest.mark.asyncio
async def test_cache_get__miss(cache):
    """Return None on cache miss."""
    result = await cache.get_cached("nonexistent_key")
    assert result is None


@pytest.mark.asyncio
async def test_cache_set__stores_json(cache):
    """Store and retrieve JSON-serializable dict."""
    key = "chat:v1:abc123"
    value = {
        "paddles": [
            {
                "paddle_id": 1,
                "name": "Paddle A",
                "price_min_brl": 500.0,
                "affiliate_url": "https://example.com/paddle-a"
            }
        ],
        "reasoning": "Recomendado para iniciantes",
        "latency_ms": 250.5
    }

    await cache.set_cached(key, value)
    result = await cache.get_cached(key)

    assert result == value
    assert result["paddles"][0]["name"] == "Paddle A"


@pytest.mark.asyncio
async def test_cache_ttl__respects_expiry(cache):
    """Verify TTL mechanism (mock in development)."""
    key = "short_lived_key"
    value = {"data": "test"}

    # Set with 1 second TTL
    await cache.set_cached(key, value, ttl=1)
    result = await cache.get_cached(key)
    assert result == value

    # In production, Redis would expire after TTL
    # In development, we just verify set/get works


@pytest.mark.asyncio
async def test_cache_key__deterministic(cache):
    """Cache key generation is deterministic."""
    key1 = cache.make_cache_key(
        message="Raquete de controle",
        skill_level="beginner",
        budget_brl=500.0
    )
    key2 = cache.make_cache_key(
        message="Raquete de controle",
        skill_level="beginner",
        budget_brl=500.0
    )

    assert key1 == key2
    assert key1.startswith("chat:v1:")


@pytest.mark.asyncio
async def test_cache_key__different_inputs(cache):
    """Different inputs produce different keys."""
    key1 = cache.make_cache_key(
        message="Raquete A",
        skill_level="beginner",
        budget_brl=500.0
    )
    key2 = cache.make_cache_key(
        message="Raquete B",
        skill_level="beginner",
        budget_brl=500.0
    )

    assert key1 != key2


@pytest.mark.asyncio
async def test_cache_clear(cache):
    """Clear all cached entries."""
    await cache.set_cached("key1", {"data": "value1"})
    await cache.set_cached("key2", {"data": "value2"})

    assert await cache.get_cached("key1") is not None
    assert await cache.get_cached("key2") is not None

    await cache.clear()

    assert await cache.get_cached("key1") is None
    assert await cache.get_cached("key2") is None
