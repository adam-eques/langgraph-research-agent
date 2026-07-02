from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import cast

logger = logging.getLogger(__name__)


class AnswerCache:
    def __init__(self, path: str = ".answer_cache.json") -> None:
        self._path = Path(path)
        self._store: dict = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            try:
                return cast(dict, json.loads(self._path.read_text()))
            except Exception:
                return {}
        return {}

    def _key(self, query: str) -> str:
        return hashlib.sha256(query.strip().lower().encode()).hexdigest()[:20]

    def get(self, query: str) -> dict | None:
        return self._store.get(self._key(query))

    def set(self, query: str, result: dict) -> None:
        self._store[self._key(query)] = result
        self._path.write_text(json.dumps(self._store, indent=2))

    def invalidate(self, query: str) -> bool:
        key = self._key(query)
        if key in self._store:
            del self._store[key]
            self._path.write_text(json.dumps(self._store, indent=2))
            return True
        return False

    @property
    def size(self) -> int:
        return len(self._store)
