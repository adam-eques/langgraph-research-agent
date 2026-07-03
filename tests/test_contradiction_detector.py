from __future__ import annotations

from research_agent.agents.contradiction_detector import detect_contradictions, has_contradictions


def test_detects_negation():
    claims = ["Python is fast", "Python is not fast"]
    contradictions = detect_contradictions(claims)
    assert len(contradictions) > 0


def test_no_contradiction():
    claims = ["Python is fast", "Java is reliable"]
    assert has_contradictions(claims) is False


def test_confidence_range():
    claims = ["The system can scale", "The system cannot scale"]
    result = detect_contradictions(claims)
    if result:
        assert 0.0 <= result[0].confidence <= 1.0


def test_empty_input():
    assert detect_contradictions([]) == []
