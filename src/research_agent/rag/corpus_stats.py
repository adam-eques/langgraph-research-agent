from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass


@dataclass
class TermStats:
    term: str
    df: int
    idf: float
    avg_tf: float


def tokenize(text: str) -> list[str]:
    return re.findall(r"\b[a-z]{2,}\b", text.lower())


class CorpusStats:
    def __init__(self) -> None:
        self._docs: list[list[str]] = []
        self._df: Counter = Counter()

    def add_document(self, text: str) -> None:
        tokens = tokenize(text)
        self._docs.append(tokens)
        for term in set(tokens):
            self._df[term] += 1

    @property
    def num_docs(self) -> int:
        return len(self._docs)

    def df(self, term: str) -> int:
        return self._df.get(term.lower(), 0)

    def idf(self, term: str) -> float:
        n = self.num_docs
        d = self.df(term)
        if n == 0 or d == 0:
            return 0.0
        return math.log((n + 1) / (d + 1)) + 1.0

    def tf(self, term: str, doc_index: int) -> float:
        if doc_index >= len(self._docs):
            return 0.0
        tokens = self._docs[doc_index]
        count = tokens.count(term.lower())
        return count / len(tokens) if tokens else 0.0

    def tfidf(self, term: str, doc_index: int) -> float:
        return self.tf(term, doc_index) * self.idf(term)

    def top_terms(self, n: int = 10) -> list[TermStats]:
        all_terms = set(self._df.keys())
        stats = []
        for term in all_terms:
            avg_tf = sum(self.tf(term, i) for i in range(self.num_docs)) / max(self.num_docs, 1)
            stats.append(TermStats(
                term=term,
                df=self.df(term),
                idf=round(self.idf(term), 4),
                avg_tf=round(avg_tf, 6),
            ))
        return sorted(stats, key=lambda s: -s.idf)[:n]

    def vocabulary_size(self) -> int:
        return len(self._df)
