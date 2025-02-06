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


class RateLimitError(ResearchAgentError):
    """Raised when the request rate limit is exceeded."""

    def __init__(self, client_id: str, retry_after: int = 60) -> None:
        self.client_id = client_id
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded for '{client_id}'. Retry after {retry_after}s.")


class TimeoutError(ResearchAgentError):
    """Raised when an agent node exceeds its time budget."""

    def __init__(self, node: str, timeout_s: float) -> None:
        super().__init__(f"Node '{node}' timed out after {timeout_s}s.")
