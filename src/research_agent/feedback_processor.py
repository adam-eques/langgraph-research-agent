from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Feedback:
    session_id: str
    query: str
    rating: int
    comment: str = ""
    helpful: bool = True
    tags: list = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not 1 <= self.rating <= 5:
            raise ValueError(f"Rating must be 1-5, got {self.rating}")


class FeedbackProcessor:
    def __init__(self, storage_path: str = "feedback.jsonl") -> None:
        self._path = Path(storage_path)
        self._entries: list[Feedback] = []

    def submit(self, feedback: Feedback) -> None:
        self._entries.append(feedback)
        with self._path.open("a") as f:
            f.write(json.dumps(asdict(feedback)) + "\n")
        logger.info(
            "Feedback submitted: session=%s rating=%d", feedback.session_id, feedback.rating
        )

    def average_rating(self) -> float:
        if not self._entries:
            return 0.0
        return sum(e.rating for e in self._entries) / len(self._entries)

    def positive_rate(self) -> float:
        if not self._entries:
            return 0.0
        return sum(1 for e in self._entries if e.helpful) / len(self._entries)

    def by_session(self, session_id: str) -> list[Feedback]:
        return [e for e in self._entries if e.session_id == session_id]

    def low_rated(self, threshold: int = 2) -> list[Feedback]:
        return [e for e in self._entries if e.rating <= threshold]
