from __future__ import annotations
from research_agent.query_normalizer import (
    normalize_query, expand_contractions, collapse_whitespace,
    remove_punctuation_edges,
)


def test_collapse_whitespace():
    assert collapse_whitespace("  hello   world  ") == "hello world"


def test_remove_punctuation_edges():
    assert remove_punctuation_edges("?What is AI?") == "?What is AI"


def test_normalize_query_lowercase():
    assert normalize_query("What IS LangGraph?") == "what is langgraph"


def test_acronym_preserved():
    result = normalize_query("How does the RAG pipeline work?")
    assert "RAG" in result


def test_expand_contractions():
    assert expand_contractions("I can't find it") == "I cannot find it"
