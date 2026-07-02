from __future__ import annotations
from research_agent.error_classifier import classify_error, is_retryable, ErrorCategory


def test_classify_timeout():
    exc = TimeoutError("Request timed out after 30s")
    result = classify_error(exc)
    assert result.category == ErrorCategory.TIMEOUT and result.retryable is True


def test_classify_rate_limit():
    exc = Exception("HTTP 429 Too Many Requests: rate limit exceeded")
    result = classify_error(exc)
    assert result.category == ErrorCategory.RATE_LIMIT


def test_classify_auth_not_retryable():
    exc = PermissionError("401 Unauthorized: invalid API key")
    result = classify_error(exc)
    assert result.category == ErrorCategory.AUTH and result.retryable is False


def test_classify_unknown():
    exc = Exception("something weird happened")
    result = classify_error(exc)
    assert result.category == ErrorCategory.UNKNOWN


def test_is_retryable_network():
    assert is_retryable(ConnectionError("network connection failed")) is True
