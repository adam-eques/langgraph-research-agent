from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class QueryHistory:
    def __init__(self, path: str = "query_history.jsonl") -> None:
        self._path = Path(path)
        self._entries: list[dict] = self._load()

    def _load(self) -> list[dict]:
        if not self._path.exists():
            return []
        try:
            return [
                json.loads(line) for line in self._path.read_text().splitlines() if line.strip()
            ]
        except Exception:
            return []

    def add(self, query: str, session_id: str = "", meta: dict | None = None) -> None:
        entry = {"query": query, "session_id": session_id, "meta": meta or {}}
        self._entries.append(entry)
        with self._path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def recent(self, n: int = 10) -> list[dict]:
        return self._entries[-n:]

    def search(self, keyword: str) -> list[dict]:
        return [e for e in self._entries if keyword.lower() in e["query"].lower()]

    def for_session(self, session_id: str) -> list[dict]:
        return [e for e in self._entries if e.get("session_id") == session_id]
