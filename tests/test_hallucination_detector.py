from __future__ import annotations

from research_agent.hallucination_detector import (
    detect_overconfident_claims,
    hallucination_risk_score,
)


def test_detect_overconfident_no_hedge():
    text = "AI is definitely always going to replace all human jobs in all sectors forever."
    flagged = detect_overconfident_claims(text)
    assert len(flagged) >= 1


def test_detect_hedged_not_flagged():
    text = "AI might possibly replace some jobs in certain sectors."
    flagged = detect_overconfident_claims(text)
    assert len(flagged) == 0


def test_hallucination_risk_with_support():
    text = "Machine learning uses data. Neural networks learn patterns."
    facts = ["machine learning uses data"]
    score = hallucination_risk_score(text, facts)
    assert 0.0 <= score <= 1.0


def test_hallucination_risk_no_facts():
    score = hallucination_risk_score("Some claim here.", [])
    assert score == 1.0
