from __future__ import annotations

from research_agent.query_rewriter import normalize_query, remove_filler_words, rewrite_for_search


def test_remove_filler_words():
    result = remove_filler_words("Please tell me about AI")
    assert "Please" not in result
    assert "tell me" not in result


def test_normalize_adds_question_mark():
    result = normalize_query("what is AI")
    assert result.endswith("?")


def test_normalize_preserves_existing_punctuation():
    result = normalize_query("What is AI?")
    assert result.count("?") == 1


def test_rewrite_for_search():
    result = rewrite_for_search("Can you explain machine learning?")
    assert not result.endswith("?")
    assert "machine learning" in result
