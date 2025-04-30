from __future__ import annotations

from research_agent.truncator import ContextTruncator


def test_truncate_short_text():
    t = ContextTruncator(max_chars=100)
    assert t.truncate("hello") == "hello"


def test_truncate_long_text():
    t = ContextTruncator(max_chars=50, overlap=0)
    result = t.truncate("a" * 100)
    assert len(result) == 50


def test_truncate_with_overlap():
    t = ContextTruncator(max_chars=10, overlap=5)
    text = "0123456789ABCDE"
    result = t.truncate(text)
    assert result.startswith("0123456789")
    assert "ABCDE" in result


def test_truncate_list():
    t = ContextTruncator(max_chars=20)
    chunks = ["aaaa", "bbbb", "cccc", "dddd", "eeee", "ffff"]
    result = t.truncate_list(chunks)
    assert len(result) < len(chunks)
    total_len = sum(len(c) for c in result)
    assert total_len <= 20
