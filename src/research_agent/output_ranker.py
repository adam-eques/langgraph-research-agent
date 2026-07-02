from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def rank_answers(
    candidates: list[dict[str, Any]],
    query: str,
    weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    w = weights or {"relevance": 0.5, "faithfulness": 0.3, "length": 0.2}
    scored = []
    q_words = set(query.lower().split())
    for c in candidates:
        answer = c.get("answer", "")
        a_words = set(answer.lower().split())
        relevance = len(q_words & a_words) / max(len(q_words), 1)
        faithfulness = c.get("faithfulness", 0.5)
        word_count = len(answer.split())
        length_score = min(1.0, word_count / 100)
        score = (
            w.get("relevance", 0.5) * relevance
            + w.get("faithfulness", 0.3) * faithfulness
            + w.get("length", 0.2) * length_score
        )
        scored.append({**c, "_score": round(score, 4)})
    return sorted(scored, key=lambda x: x["_score"], reverse=True)
