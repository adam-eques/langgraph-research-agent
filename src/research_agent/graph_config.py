from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphConfig:
    """Runtime configuration for the LangGraph research agent."""
    model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.0
    max_tokens: int = 4096
    use_supervisor: bool = False
    use_rag: bool = True
    use_fact_checker: bool = True
    use_citation_verifier: bool = False
    use_planner: bool = False
    max_iterations: int = 10
    checkpointing: bool = False
    collection: str = "research_docs"
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "use_supervisor": self.use_supervisor,
            "use_rag": self.use_rag,
            "use_fact_checker": self.use_fact_checker,
            "use_citation_verifier": self.use_citation_verifier,
            "use_planner": self.use_planner,
            "max_iterations": self.max_iterations,
            "checkpointing": self.checkpointing,
            "collection": self.collection,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "GraphConfig":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
