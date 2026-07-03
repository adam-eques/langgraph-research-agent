from __future__ import annotations

import hashlib
import logging
from typing import Any

logger = logging.getLogger(__name__)


class SemanticCache:
    """Simple in-memory semantic cache using normalized query keys."""

    def __init__(self, max_size: int = 256) -> None:
        self._store: dict[str, Any] = {}
        self._order: list[str] = []
        self.max_size = max_size

    def _key(self, query: str) -> str:
        normalized = " ".join(query.strip().lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:24]

    def get(self, query: str) -> Any | None:
        key = self._key(query)
        return self._store.get(key)

    def set(self, query: str, value: Any) -> None:
        key = self._key(query)
        if key not in self._store:
            if len(self._order) >= self.max_size:
                oldest = self._order.pop(0)
                self._store.pop(oldest, None)
                logger.debug("Evicted oldest entry from semantic cache")
            self._order.append(key)
        self._store[key] = value

    def invalidate(self, query: str) -> bool:
        key = self._key(query)
        if key in self._store:
            self._store.pop(key)
            self._order.remove(key)
            return True
        return False

    def clear(self) -> None:
        self._store.clear()
        self._order.clear()

    @property
    def size(self) -> int:
        return len(self._store)
