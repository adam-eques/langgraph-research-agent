from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


def precision_at_k(retrieved: list[str], relevant: list[str], k: int) -> float:
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for doc in top_k if doc in relevant)
    return hits / k


def recall_at_k(retrieved: list[str], relevant: list[str], k: int) -> float:
    if not relevant:
        return 1.0
    top_k = retrieved[:k]
    hits = sum(1 for doc in top_k if doc in relevant)
    return hits / len(relevant)


def mean_reciprocal_rank(retrieved: list[str], relevant: list[str]) -> float:
    for i, doc in enumerate(retrieved, 1):
        if doc in relevant:
            return 1.0 / i
    return 0.0


def evaluate_retrieval(
    retrieved: list[str], relevant: list[str], k: int = 5
) -> dict[str, float]:
    return {
        "precision_at_k": precision_at_k(retrieved, relevant, k),
        "recall_at_k": recall_at_k(retrieved, relevant, k),
        "mrr": mean_reciprocal_rank(retrieved, relevant),
    }
