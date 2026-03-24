from __future__ import annotations

from research_agent.answer_validator import check_answer_completeness, is_answer_acceptable


def test_check_completeness_keys():
    result = check_answer_completeness("What is machine learning?", "Machine learning is a subset of AI.")
    assert "word_count" in result
    assert "query_coverage" in result
    assert "passed" in result


def test_check_empty_answer():
    result = check_answer_completeness("What is AI?", "")
    assert result["not_empty"] is False


def test_is_acceptable_true():
    query = "What is machine learning and artificial intelligence?"
    answer = "Machine learning is a method of artificial intelligence that allows computers to learn from data."
    assert is_answer_acceptable(query, answer) is True


def test_is_acceptable_empty():
    assert is_answer_acceptable("What is AI?", "") is False
