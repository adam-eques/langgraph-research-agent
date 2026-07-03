from __future__ import annotations

import logging
from typing import ClassVar

logger = logging.getLogger(__name__)


class QueryRouter:
    """Route research queries to the appropriate pipeline based on characteristics."""

    KEYWORD_SIGNALS: ClassVar[dict[str, list[str]]] = {
        "rag": ["document", "file", "pdf", "report", "ingested", "uploaded"],
        "web": ["latest", "recent", "today", "news", "2024", "2025", "current"],
        "supervisor": ["compare", "analyze", "comprehensive", "deep dive", "multi-step"],
    }

    def __init__(self, default: str = "linear") -> None:
        self.default = default
        self._stats: dict[str, int] = {"rag": 0, "web": 0, "supervisor": 0, "linear": 0}

    def route(self, query: str) -> str:
        q = query.lower()
        for mode, signals in self.KEYWORD_SIGNALS.items():
            if any(s in q for s in signals):
                self._stats[mode] = self._stats.get(mode, 0) + 1
                logger.debug("Routing query to %s mode based on signals", mode)
                return mode
        self._stats[self.default] += 1
        return self.default

    @property
    def stats(self) -> dict[str, int]:
        return dict(self._stats)
