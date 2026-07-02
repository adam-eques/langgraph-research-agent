from __future__ import annotations

from research_agent.document_scorer import filter_low_quality, score_document_quality


def test_empty_document():
    assert score_document_quality("") == 0.0


def test_quality_score_range():
    text = "Machine learning is a subfield of artificial intelligence. " * 10
    score = score_document_quality(text)
    assert 0.0 <= score <= 1.0


def test_quality_short_document_is_low():
    score = score_document_quality("hi")
    assert score < 0.5


def test_filter_low_quality():
    docs = [
        "hi",
        "Machine learning is a subfield of AI that enables computers to learn from data. " * 5,
    ]
    result = filter_low_quality(docs)
    assert len(result) == 1
    assert "Machine learning" in result[0]
