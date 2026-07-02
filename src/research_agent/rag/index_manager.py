from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class IndexManager:
    def __init__(self) -> None:
        self._collections: dict[str, dict] = {}

    def create(self, name: str, meta: dict | None = None) -> None:
        if name in self._collections:
            return
        self._collections[name] = {"name": name, "doc_count": 0, "meta": meta or {}}

    def drop(self, name: str) -> bool:
        if name not in self._collections:
            return False
        del self._collections[name]
        return True

    def list_collections(self) -> list[str]:
        return sorted(self._collections.keys())

    def exists(self, name: str) -> bool:
        return name in self._collections

    def increment_doc_count(self, name: str, by: int = 1) -> None:
        if name in self._collections:
            self._collections[name]["doc_count"] += by

    def stats(self, name: str) -> dict | None:
        return self._collections.get(name)
