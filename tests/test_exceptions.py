from __future__ import annotations

import pytest

from research_agent.exceptions import (
    CacheError,
    ConfigError,
    EvalError,
    IngestionError,
    LLMError,
    ResearchAgentError,
    RetrievalError,
)


def test_ingestion_error_message():
    exc = IngestionError("report.pdf", "file not found")
    assert "report.pdf" in str(exc)
    assert "file not found" in str(exc)
    assert exc.path == "report.pdf"
    assert exc.reason == "file not found"


def test_config_error_message():
    exc = ConfigError("ANTHROPIC_API_KEY")
    assert "ANTHROPIC_API_KEY" in str(exc)
    assert ".env" in str(exc)


def test_all_errors_are_subclasses():
    for exc_class in (RetrievalError, LLMError, IngestionError, CacheError, EvalError, ConfigError):
        assert issubclass(exc_class, ResearchAgentError)
        assert issubclass(exc_class, Exception)


def test_can_catch_as_base():
    with pytest.raises(ResearchAgentError):
        raise LLMError("model unavailable")


def test_retrieval_error_is_catchable():
    with pytest.raises(RetrievalError):
        raise RetrievalError("collection not found")


def test_ingestion_error_path():
    from research_agent.exceptions import IngestionError

    exc = IngestionError("/docs/file.pdf", "permission denied")
    assert exc.path == "/docs/file.pdf"


def test_rate_limit_error():
    from research_agent.exceptions import RateLimitError

    exc = RateLimitError("user123", retry_after=30)
    assert exc.retry_after == 30
    assert "30s" in str(exc)
