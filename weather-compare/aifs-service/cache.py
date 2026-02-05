"""
In-memory cache for AIFS forecast data.

Simple TTL-based cache to avoid re-processing GRIB data for repeated requests.
"""

import time
import logging
from typing import Any, Optional
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)

# Default TTL: 1 hour (AIFS updates every 6 hours, so 1 hour cache is reasonable)
DEFAULT_TTL = 3600


@dataclass
class CacheEntry:
    """Cache entry with value and expiration time."""

    value: Any
    expires_at: float


class ForecastCache:
    """Thread-safe TTL cache for forecast data."""

    def __init__(self, ttl: int = DEFAULT_TTL, max_size: int = 1000):
        """
        Initialize cache.

        Args:
            ttl: Time-to-live in seconds
            max_size: Maximum number of entries
        """
        self._cache: dict[str, CacheEntry] = {}
        self._ttl = ttl
        self._max_size = max_size
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if exists and not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if time.time() > entry.expires_at:
                # Expired, remove it
                del self._cache[key]
                return None

            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional custom TTL (uses default if not specified)
        """
        with self._lock:
            # Evict oldest entries if at capacity
            if len(self._cache) >= self._max_size:
                self._evict_expired()
                if len(self._cache) >= self._max_size:
                    # Remove oldest entry
                    oldest_key = min(
                        self._cache.keys(),
                        key=lambda k: self._cache[k].expires_at,
                    )
                    del self._cache[oldest_key]

            expires_at = time.time() + (ttl if ttl is not None else self._ttl)
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> bool:
        """
        Delete entry from cache.

        Args:
            key: Cache key

        Returns:
            True if entry was deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Clear all entries from cache."""
        with self._lock:
            self._cache.clear()

    def _evict_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if v.expires_at < now]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    def __contains__(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None

    def __len__(self) -> int:
        """Return number of entries (including expired)."""
        return len(self._cache)

    @property
    def stats(self) -> dict:
        """Get cache statistics."""
        with self._lock:
            now = time.time()
            valid_count = sum(1 for v in self._cache.values() if v.expires_at > now)
            return {
                "total_entries": len(self._cache),
                "valid_entries": valid_count,
                "expired_entries": len(self._cache) - valid_count,
                "max_size": self._max_size,
                "ttl": self._ttl,
            }


# Global cache instance for forecast data
forecast_cache = ForecastCache(ttl=DEFAULT_TTL, max_size=1000)


def make_cache_key(lat: float, lon: float, days: int = 10) -> str:
    """
    Create a cache key from coordinates.

    Rounds to 2 decimal places (~1km precision) to increase cache hits.
    """
    return f"{lat:.2f},{lon:.2f},{days}"
