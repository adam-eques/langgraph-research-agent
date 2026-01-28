from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AggregatedResult:
    query: str
    answers: list[str]
    sources: list[str]
    confidence: float
    metadata: dict

    @property
    def best_answer(self) -> str:
        return self.answers[0] if self.answers else ""

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "best_answer": self.best_answer,
            "answers": self.answers,
            "sources": self.sources,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


def aggregate_results(
    query: str,
    results: list[dict[str, Any]],
    answer_key: str = "answer",
    source_key: str = "source",
    confidence_key: str = "confidence",
) -> AggregatedResult:
    answers = [r[answer_key] for r in results if answer_key in r and r[answer_key]]
    sources = list(dict.fromkeys(r[source_key] for r in results if source_key in r))
    confidences = [r[confidence_key] for r in results if confidence_key in r and isinstance(r[confidence_key], (int, float))]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5
    return AggregatedResult(
        query=query,
        answers=answers,
        sources=sources,
        confidence=avg_confidence,
        metadata={"count": len(results), "sources_count": len(sources)},
    )


def merge_answers(answers: list[str], separator: str = "\n\n") -> str:
    seen: set[str] = set()
    unique = []
    for a in answers:
        normalized = a.strip()
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique.append(normalized)
    return separator.join(unique)
