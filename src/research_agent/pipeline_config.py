from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    max_search_results: int = 10
    max_context_tokens: int = 6000
    enable_web_search: bool = True
    enable_rag: bool = True
    enable_fact_check: bool = True
    enable_citation_verify: bool = True
    retrieval_top_k: int = 5
    rerank_top_k: int = 3
    llm_model: str = "claude-3-5-sonnet-20241022"
    temperature: float = 0.3
    timeout_seconds: float = 120.0
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "max_search_results": self.max_search_results,
            "max_context_tokens": self.max_context_tokens,
            "enable_web_search": self.enable_web_search,
            "enable_rag": self.enable_rag,
            "enable_fact_check": self.enable_fact_check,
            "enable_citation_verify": self.enable_citation_verify,
            "retrieval_top_k": self.retrieval_top_k,
            "rerank_top_k": self.rerank_top_k,
            "llm_model": self.llm_model,
            "temperature": self.temperature,
            "timeout_seconds": self.timeout_seconds,
            "tags": self.tags,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PipelineConfig":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def with_overrides(self, **kwargs) -> "PipelineConfig":
        from dataclasses import replace
        return replace(self, **kwargs)
