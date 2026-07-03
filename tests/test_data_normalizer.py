from __future__ import annotations

from research_agent.data_normalizer import (
    normalize_boolean,
    normalize_list,
    normalize_number,
    normalize_record,
    normalize_string,
)


def test_normalize_string():
    assert normalize_string("  hello   world  ") == "hello world"


def test_normalize_number():
    assert normalize_number("1,234.5") == 1234.5
    assert normalize_number("bad", default=0.0) == 0.0


def test_normalize_boolean():
    assert normalize_boolean("yes") is True and normalize_boolean("false") is False


def test_normalize_list_from_csv():
    assert normalize_list("a, b, c") == ["a", "b", "c"]


def test_normalize_record():
    schema = {"name": "str", "score": "float", "active": "bool", "tags": "list"}
    raw = {"name": "  AI  ", "score": "0.9", "active": "yes", "tags": "python,ai"}
    result = normalize_record(raw, schema)
    assert result["name"] == "AI" and result["score"] == 0.9 and result["active"] is True
