from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class FactStore:
    """Persist extracted facts with source attribution for cross-turn reuse."""

    def __init__(self, path: str = "facts.jsonl") -> None:
        self._path = Path(path)
        self._facts: list[dict[str, Any]] = self._load()

    def _load(self) -> list[dict]:
        if not self._path.exists():
            return []
        try:
            return [json.loads(l) for l in self._path.read_text().splitlines() if l.strip()]
        except Exception:
            return []

    def add(self, fact: str, source: str, confidence: float = 1.0) -> None:
        entry = {"fact": fact, "source": source, "confidence": confidence}
        self._facts.append(entry)
        with self._path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        logger.debug("Fact stored: %s (source=%s, conf=%.2f)", fact[:60], source, confidence)

    def search(self, keyword: str) -> list[dict]:
        kw = keyword.lower()
        return [f for f in self._facts if kw in f["fact"].lower()]

    def all_facts(self) -> list[dict]:
        return list(self._facts)

    def high_confidence(self, threshold: float = 0.8) -> list[dict]:
        return [f for f in self._facts if f["confidence"] >= threshold]
