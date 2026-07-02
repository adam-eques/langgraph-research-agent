from __future__ import annotations

import math
import re
from typing import Any


def tf(term: str, document: str) -> float:
    words = document.lower().split()
    count = words.count(term.lower())
    return count / len(words) if words else 0.0


def idf(term: str, documents: list[str]) -> float:
    n = len(documents)
    docs_with_term = sum(1 for d in documents if term.lower() in d.lower())
    if docs_with_term == 0:
        return 0.0
    return math.log((n + 1) / (docs_with_term + 1)) + 1


def bm25_score(
    query: str, document: str, all_docs: list[str], k1: float = 1.5, b: float = 0.75
) -> float:
    terms = re.findall(r"\b\w+\b", query.lower())
    avg_dl = sum(len(d.split()) for d in all_docs) / max(len(all_docs), 1)
    dl = len(document.split())
    score = 0.0
    for term in terms:
        tf_val = tf(term, document)
        idf_val = idf(term, all_docs)
        numerator = tf_val * (k1 + 1)
        denominator = tf_val + k1 * (1 - b + b * dl / avg_dl)
        score += idf_val * numerator / max(denominator, 1e-9)
    return score


def rank_documents(
    query: str,
    documents: list[dict[str, Any]],
    content_key: str = "content",
) -> list[dict[str, Any]]:
    texts = [d.get(content_key, "") for d in documents]
    scored = [
        {**doc, "_bm25": bm25_score(query, texts[i], texts)} for i, doc in enumerate(documents)
    ]
    return sorted(scored, key=lambda d: d["_bm25"], reverse=True)
