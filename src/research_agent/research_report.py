from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResearchReport:
    query: str
    answer: str
    citations: list[dict] = field(default_factory=list)
    research_notes: list[str] = field(default_factory=list)
    confidence: float = 0.0
    model: str = ""
    tokens_used: int = 0
    version: str = "1.0"

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "citations": self.citations,
            "research_notes": self.research_notes,
            "confidence": self.confidence,
            "model": self.model,
            "tokens_used": self.tokens_used,
            "version": self.version,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "ResearchReport":
        return cls(
            query=data.get("query", ""),
            answer=data.get("answer", ""),
            citations=data.get("citations", []),
            research_notes=data.get("research_notes", []),
            confidence=data.get("confidence", 0.0),
            model=data.get("model", ""),
            tokens_used=data.get("tokens_used", 0),
        )
