from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    key: str
    created_at: float = field(default_factory=time.monotonic)
    access_count: int = 0
    tags: list[str] = field(default_factory=list)


class CacheInvalidator:
    def __init__(self) -> None:
        self._entries: dict[str, CacheEntry] = {}
        self._tag_index: dict[str, set[str]] = {}

    def register(self, key: str, tags: list[str] | None = None) -> None:
        entry = CacheEntry(key=key, tags=tags or [])
        self._entries[key] = entry
        for tag in entry.tags:
            self._tag_index.setdefault(tag, set()).add(key)

    def invalidate(self, key: str) -> bool:
        entry = self._entries.pop(key, None)
        if entry:
            for tag in entry.tags:
                self._tag_index.get(tag, set()).discard(key)
            logger.debug("Invalidated cache key: %s", key)
            return True
        return False

    def invalidate_by_tag(self, tag: str) -> int:
        keys = list(self._tag_index.pop(tag, set()))
        count = 0
        for key in keys:
            if self.invalidate(key):
                count += 1
        return count

    def invalidate_older_than(self, max_age_seconds: float) -> int:
        now = time.monotonic()
        stale = [k for k, e in self._entries.items() if now - e.created_at > max_age_seconds]
        for key in stale:
            self.invalidate(key)
        return len(stale)

    def keys(self) -> list[str]:
        return list(self._entries.keys())

    def __len__(self) -> int:
        return len(self._entries)
