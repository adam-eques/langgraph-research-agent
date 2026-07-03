from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, cast

logger = logging.getLogger(__name__)


class KnowledgeBase:
    def __init__(self, path: str = "knowledge.json") -> None:
        self._path = Path(path)
        self._store: dict[str, Any] = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            try:
                return cast(dict, json.loads(self._path.read_text()))
            except Exception:
                return {}
        return {}

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value
        self._path.write_text(json.dumps(self._store, indent=2))

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            self._path.write_text(json.dumps(self._store, indent=2))
            return True
        return False

    def keys(self) -> list[str]:
        return list(self._store.keys())

    def clear(self) -> None:
        self._store.clear()
        self._path.write_text("{}")
