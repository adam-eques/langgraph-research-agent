from __future__ import annotations

import hashlib
import json
import time
from typing import Any


class ResponseCache:
    def __init__(self, ttl: float = 600.0, max_entries: int = 512) -> None:
        self._ttl = ttl
        self._max = max_entries
        self._store: dict[str, tuple[Any, float]] = {}

    def _key(self, prompt: str, model: str) -> str:
        raw = json.dumps({"prompt": prompt, "model": model}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:24]

    def get(self, prompt: str, model: str = "") -> Any | None:
        key = self._key(prompt, model)
        entry = self._store.get(key)
        if entry is None:
            return None
        value, ts = entry
        if time.perf_counter() - ts > self._ttl:
            del self._store[key]
            return None
        return value

    def set(self, prompt: str, response: Any, model: str = "") -> None:
        if len(self._store) >= self._max:
            oldest = min(self._store, key=lambda k: self._store[k][1])
            del self._store[oldest]
        key = self._key(prompt, model)
        self._store[key] = (response, time.perf_counter())

    def clear(self) -> None:
        self._store.clear()

    @property
    def size(self) -> int:
        return len(self._store)

    def hit_rate(self, hits: int, misses: int) -> float:
        total = hits + misses
        return hits / total if total > 0 else 0.0
