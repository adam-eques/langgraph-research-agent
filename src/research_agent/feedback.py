from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FeedbackStore:
    """Persist and query user feedback on research responses."""

    def __init__(self, path: str = "feedback.jsonl") -> None:
        self._path = Path(path)

    def record(self, query: str, rating: int, comment: str = "") -> None:
        entry = {"query": query, "rating": rating, "comment": comment}
        with self._path.open("a") as f:
            f.write(json.dumps(entry) + "\n")

    def all_feedback(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []
        return [json.loads(line) for line in self._path.read_text().splitlines() if line.strip()]

    def average_rating(self) -> float:
        fb = self.all_feedback()
        if not fb:
            return 0.0
        return sum(f["rating"] for f in fb) / len(fb)

    def low_rated(self, threshold: int = 3) -> list[dict]:
        return [f for f in self.all_feedback() if f["rating"] <= threshold]
