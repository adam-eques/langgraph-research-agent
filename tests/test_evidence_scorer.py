from __future__ import annotations

from research_agent.evidence_scorer import score_evidence_strength, classify_evidence


def test_strong_evidence():
    score = score_evidence_strength("A peer-reviewed study published in Nature shows the results.")
    assert score > 0.5


def test_weak_evidence():
    score = score_evidence_strength("Some say it might possibly be true.")
    assert score < 0.5


def test_classify_strong():
    assert classify_evidence(0.9) == "strong"


def test_classify_moderate():
    assert classify_evidence(0.6) == "moderate"


def test_classify_weak():
    assert classify_evidence(0.3) == "weak"
