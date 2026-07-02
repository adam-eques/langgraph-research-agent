from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class DocumentRegistry:
    """Track indexed documents to prevent duplicate ingestion."""

    def __init__(self, registry_path: str = ".doc_registry.json") -> None:
        self._path = Path(registry_path)
        self._data: dict[str, dict] = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text())
            except Exception:
                return {}
        return {}

    def _hash(self, path: str) -> str:
        content = Path(path).read_bytes() if Path(path).exists() else path.encode()
        return hashlib.sha256(content).hexdigest()[:16]

    def register(self, path: str, collection: str, meta: dict | None = None) -> str:
        key = self._hash(path)
        self._data[key] = {"path": path, "collection": collection, "meta": meta or {}}
        self._path.write_text(json.dumps(self._data, indent=2))
        return key

    def is_registered(self, path: str) -> bool:
        return self._hash(path) in self._data

    def all_docs(self) -> list[dict[str, Any]]:
        return list(self._data.values())
