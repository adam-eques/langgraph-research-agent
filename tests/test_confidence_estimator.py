from __future__ import annotations

from research_agent.agents.confidence_estimator import confidence_label, estimate_confidence


def test_high_confidence_words_increase_score():
    score = estimate_confidence("This is confirmed and established by research.", [])
    assert score > 0.5


def test_low_confidence_words_decrease():
    score = estimate_confidence("This might possibly be unclear and uncertain.", [])
    assert score <= 0.5


def test_citation_bonus():
    citations = [{"source": f"source{i}"} for i in range(5)]
    s_no_cite = estimate_confidence("Some answer here.", [])
    s_with_cite = estimate_confidence("Some answer here.", citations)
    assert s_with_cite > s_no_cite


def test_confidence_label():
    assert confidence_label(0.9) == "high"
    assert confidence_label(0.6) == "medium"
    assert confidence_label(0.3) == "low"
