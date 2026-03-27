"""Redis caching layer for chat queries."""

import hashlib
from typing import Optional, Dict, Any


class RedisCache:
    """Simple in-memory cache for development (production uses Redis)."""

    def __init__(self, redis_url: Optional[str] = None):
        """Initialize cache.

        Args:
            redis_url: Redis connection URL (for production)
        """
        self.redis_url = redis_url
        self._memory_cache: Dict[str, Any] = {}

    async def get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached value by key.

        Args:
            key: Cache key (MD5 hash format)

        Returns:
            Cached dict or None if miss
        """
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
        # In production, Redis handles TTL automatically
        # For now, store indefinitely (development)
        self._memory_cache[key] = value

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
        self._memory_cache.clear()
