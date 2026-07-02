from __future__ import annotations

from research_agent.relevance_filter import (
    compute_keyword_overlap,
    filter_relevant,
    rank_by_relevance,
)


def test_keyword_overlap_high():
    score = compute_keyword_overlap("machine learning AI", "machine learning and AI research")
    assert score > 0.5


def test_keyword_overlap_low():
    score = compute_keyword_overlap("quantum computing", "the weather is nice today")
    assert score == 0.0


def test_filter_relevant():
    docs = [
        "machine learning is a subset of AI",
        "the sky is blue today",
    ]
    result = filter_relevant("machine learning AI", docs, threshold=0.2)
    assert len(result) == 1
    assert "machine learning" in result[0]


def test_rank_by_relevance():
    docs = ["AI research paper", "sports news"]
    ranked = rank_by_relevance("AI research", docs)
    assert "AI research" in ranked[0][1]
