from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class PromptVersioner:
    """Track and version prompt templates across experiments."""

    def __init__(self, store_path: str = ".prompt_versions.json") -> None:
        self._path = Path(store_path)
        self._store: dict[str, list[dict]] = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text())
            except Exception:
                pass
        return {}

    def save(self) -> None:
        self._path.write_text(json.dumps(self._store, indent=2))

    def register(self, name: str, template: str, meta: dict | None = None) -> str:
        digest = hashlib.sha256(template.encode()).hexdigest()[:12]
        entry = {"digest": digest, "template": template, "meta": meta or {}}
        self._store.setdefault(name, [])
        digests = [e["digest"] for e in self._store[name]]
        if digest not in digests:
            self._store[name].append(entry)
        return digest

    def get_latest(self, name: str) -> str | None:
        versions = self._store.get(name, [])
        return versions[-1]["template"] if versions else None

    def list_versions(self, name: str) -> list[str]:
        return [e["digest"] for e in self._store.get(name, [])]
