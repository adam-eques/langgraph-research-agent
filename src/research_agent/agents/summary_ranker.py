from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class RankedSummary:
    text: str
    score: float
    length: int
    keyword_hits: int
    rank: int = 0

    def to_dict(self) -> dict:
        return {
            "text": self.text[:200],
            "score": round(self.score, 4),
            "length": self.length,
            "keyword_hits": self.keyword_hits,
            "rank": self.rank,
        }


def _count_keyword_hits(text: str, keywords: list[str]) -> int:
    t = text.lower()
    return sum(1 for kw in keywords if kw.lower() in t)


def _sentence_count(text: str) -> int:
    return max(1, len(re.split(r"[.!?]+", text.strip())))


def score_summary(
    text: str,
    keywords: list[str],
    ideal_length: int = 200,
    length_weight: float = 0.3,
    keyword_weight: float = 0.5,
    coverage_weight: float = 0.2,
) -> float:
    kw_hits = _count_keyword_hits(text, keywords)
    kw_score = min(kw_hits / max(len(keywords), 1), 1.0)

    length_penalty = abs(len(text) - ideal_length) / max(ideal_length, 1)
    length_score = max(0.0, 1.0 - length_penalty)

    sent_count = _sentence_count(text)
    coverage_score = min(sent_count / 5, 1.0)

    return (
        keyword_weight * kw_score
        + length_weight * length_score
        + coverage_weight * coverage_score
    )


def rank_summaries(
    summaries: list[str],
    keywords: list[str],
    ideal_length: int = 200,
) -> list[RankedSummary]:
    scored = [
        RankedSummary(
            text=s,
            score=score_summary(s, keywords, ideal_length),
            length=len(s),
            keyword_hits=_count_keyword_hits(s, keywords),
        )
        for s in summaries
    ]
    scored.sort(key=lambda r: -r.score)
    for i, r in enumerate(scored):
        r.rank = i + 1
    return scored


def select_best(summaries: list[str], keywords: list[str]) -> str | None:
    ranked = rank_summaries(summaries, keywords)
    return ranked[0].text if ranked else None
