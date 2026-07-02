from __future__ import annotations

import hashlib
import logging

logger = logging.getLogger(__name__)


class EmbeddingCache:
    def __init__(self, max_size: int = 1024) -> None:
        self._cache: dict[str, list[float]] = {}
        self._order: list[str] = []
        self.max_size = max_size

    def _key(self, text: str) -> str:
        return hashlib.sha256(text.strip().encode()).hexdigest()[:20]

    def get(self, text: str) -> list[float] | None:
        return self._cache.get(self._key(text))

    def set(self, text: str, embedding: list[float]) -> None:
        key = self._key(text)
        if key not in self._cache:
            if len(self._order) >= self.max_size:
                oldest = self._order.pop(0)
                self._cache.pop(oldest, None)
            self._order.append(key)
        self._cache[key] = embedding

    def __len__(self) -> int:
        return len(self._cache)
