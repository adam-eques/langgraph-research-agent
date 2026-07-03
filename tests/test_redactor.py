from __future__ import annotations

from research_agent.redactor import redact


def test_redacts_api_key():
    data = {"api_key": "sk-abc123", "query": "hello"}
    result = redact(data)
    assert result["api_key"] == "[REDACTED]"
    assert result["query"] == "hello"


def test_redacts_nested_secret():
    data = {"auth": {"token": "abc", "user": "arman"}}
    result = redact(data)
    assert result["auth"]["token"] == "[REDACTED]"
    assert result["auth"]["user"] == "arman"


def test_leaves_non_sensitive():
    data = {"model": "claude", "temperature": 0.0}
    result = redact(data)
    assert result == data


def test_handles_list():
    data = [{"api_key": "x"}, {"query": "y"}]
    result = redact(data)
    assert result[0]["api_key"] == "[REDACTED]"
    assert result[1]["query"] == "y"
