from __future__ import annotations


class ResearchAgentError(Exception):
    """Base exception for all research agent errors."""


class RetrievalError(ResearchAgentError):
    """Raised when document retrieval fails."""


class LLMError(ResearchAgentError):
    """Raised when an LLM call fails after retries."""


class IngestionError(ResearchAgentError):
    """Raised when document ingestion fails."""

    def __init__(self, path: str, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"Failed to ingest '{path}': {reason}")


class CacheError(ResearchAgentError):
    """Raised when cache read/write fails."""


class EvalError(ResearchAgentError):
    """Raised when evaluation pipeline encounters an error."""


class ConfigError(ResearchAgentError):
    """Raised when required configuration is missing."""

    def __init__(self, key: str) -> None:
        super().__init__(f"Required config key '{key}' is not set. Check your .env file.")
