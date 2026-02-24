from __future__ import annotations
from research_agent.truncation_policy import (
    truncate, TruncationPolicy, TruncationStrategy, truncate_list,
)


def test_no_truncation_if_short():
    p = TruncationPolicy(max_chars=100)
    assert truncate("short text", p) == "short text"


def test_tail_truncation():
    p = TruncationPolicy(max_chars=10, strategy=TruncationStrategy.TAIL)
    result = truncate("0123456789extra", p)
    assert result.endswith("...") and len(result) <= 10


def test_head_truncation():
    p = TruncationPolicy(max_chars=10, strategy=TruncationStrategy.HEAD)
    result = truncate("0123456789extra", p)
    assert result.startswith("...")


def test_middle_truncation():
    p = TruncationPolicy(max_chars=12, strategy=TruncationStrategy.MIDDLE)
    result = truncate("0123456789abcdefg", p)
    assert "..." in result and len(result) <= 12


def test_truncate_list():
    p = TruncationPolicy(max_chars=5)
    items = ["hello world", "foo bar baz"]
    result = truncate_list(items, max_items=2, policy=p)
    assert all(len(r) <= 5 for r in result)
