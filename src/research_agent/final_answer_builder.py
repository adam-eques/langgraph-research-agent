from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FinalAnswer:
    query: str
    answer: str
    citations: list[dict] = field(default_factory=list)
    confidence: float = 0.8
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "query": self.query,
            "answer": self.answer,
            "citations": self.citations,
            "confidence": round(self.confidence, 4),
            "metadata": self.metadata,
            "has_citations": len(self.citations) > 0,
        }

    def format_with_citations(self) -> str:
        if not self.citations:
            return self.answer
        refs = "\n".join(
            f"[{i+1}] {c.get('source', 'unknown')}: {c.get('excerpt', '')[:100]}"
            for i, c in enumerate(self.citations)
        )
        return f"{self.answer}\n\nReferences:\n{refs}"


def build_final_answer(
    query: str,
    research_notes: list[str],
    citations: list[dict],
    model_answer: str = "",
    confidence: float = 0.8,
) -> FinalAnswer:
    if model_answer:
        answer = model_answer
    elif research_notes:
        answer = " ".join(n.strip() for n in research_notes[:3] if n.strip())
    else:
        answer = "No answer found."

    deduped_citations = []
    seen_sources: set[str] = set()
    for c in citations:
        src = c.get("source", "")
        if src not in seen_sources:
            seen_sources.add(src)
            deduped_citations.append(c)

    return FinalAnswer(
        query=query,
        answer=answer,
        citations=deduped_citations[:10],
        confidence=confidence,
        metadata={"note_count": len(research_notes), "citation_count": len(deduped_citations)},
    )
