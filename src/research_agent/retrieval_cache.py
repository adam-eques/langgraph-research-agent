from __future__ import annotations

import hashlib
import time
from typing import Any, cast


class RetrievalCache:
    def __init__(self, ttl: float = 300.0, max_size: int = 256) -> None:
        self._ttl = ttl
        self._max_size = max_size
        self._store: dict[str, tuple[Any, float]] = {}

    def _key(self, query: str, collection: str) -> str:
        raw = f"{query.strip().lower()}|{collection}"
        return hashlib.sha256(raw.encode()).hexdigest()[:24]

    def get(self, query: str, collection: str = "default") -> list | None:
        key = self._key(query, collection)
        entry = self._store.get(key)
        if entry is None:
            return None
        result, ts = entry
        if time.monotonic() - ts > self._ttl:
            del self._store[key]
            return None
        return cast(list[Any] | None, result)

    def set(self, query: str, results: list, collection: str = "default") -> None:
        if len(self._store) >= self._max_size:
            oldest = min(self._store, key=lambda k: self._store[k][1])
            del self._store[oldest]
        key = self._key(query, collection)
        self._store[key] = (results, time.monotonic())

    def invalidate(self, query: str, collection: str = "default") -> bool:
        key = self._key(query, collection)
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)
