"""Result cache for research pipeline outputs — in-memory LRU and Redis backends."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Any

logger = logging.getLogger(__name__)

_BACKEND_ENV = "CACHE_BACKEND"
_TTL_ENV = "CACHE_TTL"
_REDIS_URL_ENV = "REDIS_URL"
_DEFAULT_REDIS_URL = "redis://localhost:6379/0"
_DEFAULT_TTL = 3600  # 1 hour
_DEFAULT_MEMORY_CAPACITY = 256  # max cached entries for in-memory LRU


def _query_hash(query: str) -> str:
    """Return a stable, URL-safe SHA-256 digest of *query*."""
    return hashlib.sha256(query.strip().lower().encode()).hexdigest()


class _BaseCacheBackend(ABC):
    """Abstract interface for result cache backends."""

    @abstractmethod
    def get(self, key: str) -> dict[str, Any] | None:
        """Return cached value or ``None`` if absent/expired."""

    @abstractmethod
    def set(self, key: str, value: dict[str, Any], ttl: int) -> None:
        """Store *value* under *key* with the given TTL (seconds)."""

    @abstractmethod
    def invalidate(self, key: str) -> None:
        """Remove *key* from the cache."""

    @abstractmethod
    def clear_all(self) -> None:
        """Remove every entry from the cache."""


class _InMemoryLRUBackend(_BaseCacheBackend):
    """Thread-unsafe LRU cache backed by an OrderedDict.

    Uses manual TTL tracking so expiry is checked on every ``get``.
    Capacity is bounded by *max_size*.
    """

    def __init__(self, max_size: int = _DEFAULT_MEMORY_CAPACITY) -> None:
        self._max_size = max_size
        # stores (value, expire_at) pairs
        self._cache: OrderedDict[str, tuple[dict[str, Any], float]] = OrderedDict()

    def get(self, key: str) -> dict[str, Any] | None:
        if key not in self._cache:
            return None
        value, expire_at = self._cache[key]
        if expire_at and time.time() > expire_at:
            del self._cache[key]
            return None
        # LRU: move to end on access
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: dict[str, Any], ttl: int) -> None:
        expire_at = (time.time() + ttl) if ttl > 0 else 0.0
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = (value, expire_at)
        if len(self._cache) > self._max_size:
            # Evict the least-recently-used entry
            evicted_key, _ = self._cache.popitem(last=False)
            logger.debug("LRU evicted key: %s", evicted_key[:16])

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear_all(self) -> None:
        self._cache.clear()


class _RedisBackend(_BaseCacheBackend):
    """Redis-backed cache using JSON-serialised values with native TTL."""

    _KEY_PREFIX = "research_agent:cache:"

    def __init__(self, redis_url: str = _DEFAULT_REDIS_URL) -> None:
        try:
            import redis  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "redis-py is required for the Redis cache backend. "
                "Install it with: pip install redis"
            ) from exc
        self._client = redis.from_url(redis_url, decode_responses=True)
        logger.info("Redis cache backend connected: %s", redis_url)

    def _key(self, key: str) -> str:
        return f"{self._KEY_PREFIX}{key}"

    def get(self, key: str) -> dict[str, Any] | None:
        raw = self._client.get(self._key(key))
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Cache: corrupted entry for key %s — removing", key[:16])
            self.invalidate(key)
            return None

    def set(self, key: str, value: dict[str, Any], ttl: int) -> None:
        serialised = json.dumps(value, default=str)
        if ttl > 0:
            self._client.setex(self._key(key), ttl, serialised)
        else:
            self._client.set(self._key(key), serialised)

    def invalidate(self, key: str) -> None:
        self._client.delete(self._key(key))

    def clear_all(self) -> None:
        pattern = f"{self._KEY_PREFIX}*"
        keys = self._client.keys(pattern)
        if keys:
            self._client.delete(*keys)


class ResultCache:
    """Caches research pipeline results by query hash to avoid re-running expensive pipelines.

    Backend is selected via the ``CACHE_BACKEND`` env var (``memory`` | ``redis``).
    Default TTL is read from ``CACHE_TTL`` env var (seconds, default 3600).

    Example
    -------
    >>> cache = ResultCache()
    >>> cache.set("What is LangGraph?", {"answer": "LangGraph is ..."})
    >>> cache.get("What is LangGraph?")
    {'answer': 'LangGraph is ...'}
    >>> cache.invalidate("What is LangGraph?")
    >>> cache.get("What is LangGraph?") is None
    True
    """

    def __init__(self) -> None:
        backend_name = os.getenv(_BACKEND_ENV, "memory").lower()
        self._default_ttl = int(os.getenv(_TTL_ENV, str(_DEFAULT_TTL)))

        if backend_name == "redis":
            redis_url = os.getenv(_REDIS_URL_ENV, _DEFAULT_REDIS_URL)
            self._backend: _BaseCacheBackend = _RedisBackend(redis_url)
            logger.info("ResultCache: using Redis backend (ttl=%ds)", self._default_ttl)
        else:
            self._backend = _InMemoryLRUBackend()
            logger.info("ResultCache: using in-memory LRU backend (ttl=%ds)", self._default_ttl)

    def get(self, query: str) -> dict[str, Any] | None:
        """Return cached result for *query*, or ``None`` if not cached / expired.

        Parameters
        ----------
        query:
            The original research query (hashed internally).
        """
        key = _query_hash(query)
        result = self._backend.get(key)
        if result is not None:
            logger.debug("Cache HIT for query: %.80s", query)
        else:
            logger.debug("Cache MISS for query: %.80s", query)
        return result

    def set(
        self,
        query: str,
        result: dict[str, Any],
        ttl: int | None = None,
    ) -> None:
        """Store *result* for *query* with the given TTL.

        Parameters
        ----------
        query:
            The original research query.
        result:
            The pipeline result dict to cache.
        ttl:
            Time-to-live in seconds.  Defaults to ``CACHE_TTL`` env var or 3600.
        """
        key = _query_hash(query)
        effective_ttl = ttl if ttl is not None else self._default_ttl
        self._backend.set(key, result, effective_ttl)
        logger.debug("Cached result for query (ttl=%ds): %.80s", effective_ttl, query)

    def invalidate(self, query: str) -> None:
        """Remove the cached result for *query*.

        Parameters
        ----------
        query:
            The query whose cached result should be deleted.
        """
        key = _query_hash(query)
        self._backend.invalidate(key)
        logger.info("Cache invalidated for query: %.80s", query)

    def clear(self) -> None:
        """Remove all entries from the cache."""
        self._backend.clear_all()
        logger.info("Cache cleared")
