from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

class SparseRetriever:
    def __init__(self) -> None:
        self._index: dict[str, list[tuple[int, float]]] = {}
        self._docs: list[str] = []

    def index(self, documents: list[str]) -> None:
        self._docs = documents
        self._index.clear()
        for doc_id, doc in enumerate(documents):
            for term, freq in self._tf(doc).items():
                self._index.setdefault(term, []).append((doc_id, freq))

    def _tf(self, text: str) -> dict[str, float]:
        words = text.lower().split()
        total = max(len(words), 1)
        counts: dict[str, int] = {}
        for w in words:
            counts[w] = counts.get(w, 0) + 1
        return {w: c / total for w, c in counts.items()}

    def retrieve(self, query: str, k: int = 5) -> list[tuple[float, str]]:
        scores: dict[int, float] = {}
        for term in query.lower().split():
            for doc_id, freq in self._index.get(term, []):
                scores[doc_id] = scores.get(doc_id, 0.0) + freq
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        return [(score, self._docs[doc_id]) for doc_id, score in ranked]
