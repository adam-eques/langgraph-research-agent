from __future__ import annotations

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class CitationIndex:
    def __init__(self) -> None:
        self._by_source: dict[str, list[dict]] = defaultdict(list)
        self._all: list[dict] = []

    def add(self, citation: dict) -> None:
        self._all.append(citation)
        source = citation.get("source", "")
        if source:
            self._by_source[source].append(citation)

    def by_source(self, source: str) -> list[dict]:
        return list(self._by_source.get(source, []))

    def all_citations(self) -> list[dict]:
        return list(self._all)

    def sources(self) -> list[str]:
        return list(self._by_source.keys())

    def top_sources(self, n: int = 5) -> list[tuple[str, int]]:
        counts = [(s, len(v)) for s, v in self._by_source.items()]
        return sorted(counts, key=lambda x: x[1], reverse=True)[:n]
