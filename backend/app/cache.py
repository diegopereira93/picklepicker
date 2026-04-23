"""Redis caching layer for chat queries."""

import json
import time
import hashlib
from typing import Optional, Dict, Any

import redis.asyncio as redis


class RedisCache:
    """Cache layer with Redis backend and in-memory fallback."""

    def __init__(self, redis_url: Optional[str] = None):
        """Initialize cache.

        Args:
            redis_url: Redis connection URL (for production).
                       When None/empty, falls back to in-memory dict.
        """
        self.redis_url = redis_url
        self._redis: Optional[redis.Redis] = None
        self._memory_cache: Dict[str, Any] = {}
        self._memory_ttl: Dict[str, float] = {}

    async def _ensure_client(self) -> Optional[redis.Redis]:
        """Lazy Redis client initialization.

        Returns:
            Redis client instance or None if no URL configured.
        """
        if self._redis is None and self.redis_url:
            self._redis = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached value by key.

        Args:
            key: Cache key (MD5 hash format)

        Returns:
            Cached dict or None if miss/expired
        """
        client = await self._ensure_client()
        if client:
            value = await client.get(key)
            return json.loads(value) if value else None

        # In-memory fallback with TTL check
        if time.time() > self._memory_ttl.get(key, 0):
            self._memory_cache.pop(key, None)
            self._memory_ttl.pop(key, None)
            return None
        return self._memory_cache.get(key)

    async def set_cached(
        self, key: str, value: Dict[str, Any], ttl: int = 3600
    ) -> None:
        """Store value in cache with TTL.

        Args:
            key: Cache key
            value: Dict to cache
            ttl: Time-to-live in seconds (default 3600s = 1 hour)
        """
        client = await self._ensure_client()
        if client:
            await client.setex(key, ttl, json.dumps(value))
        else:
            # In-memory fallback
            self._memory_cache[key] = value
            self._memory_ttl[key] = time.time() + ttl

    def make_cache_key(
        self, message: str, skill_level: str, budget_brl: float
    ) -> str:
        """Generate deterministic cache key.

        Args:
            message: Chat message
            skill_level: User skill level
            budget_brl: Budget in BRL

        Returns:
            Cache key: f"chat:v1:{md5_hash}"
        """
        key_str = f"{message}:{skill_level}:{budget_brl}"
        md5_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"chat:v1:{md5_hash}"

    async def clear(self) -> None:
        """Clear all cached entries (for testing)."""
        client = await self._ensure_client()
        if client:
            await client.flushdb()
        self._memory_cache.clear()
        self._memory_ttl.clear()
