from __future__ import annotations
from research_agent.agents.hypothesis_generator import (
    Hypothesis,
    extract_causal_pairs,
    generate_hypotheses,
    filter_testable,
    rank_by_confidence,
)


def test_extract_causal_pairs():
    text = "High temperature causes faster reactions in most experiments."
    pairs = extract_causal_pairs(text)
    assert len(pairs) >= 1
    assert any("temperature" in p[0].lower() for p in pairs)


def test_generate_hypotheses_basic():
    notes = [
        "Exercise increases cardiovascular health significantly.",
        "Stress leads to poor sleep quality.",
    ]
    hyps = generate_hypotheses(notes)
    assert len(hyps) >= 1
    assert all(isinstance(h, Hypothesis) for h in hyps)


def test_generate_hypotheses_max():
    notes = [
        f"Factor{i} causes outcome{i}." for i in range(10)
    ]
    hyps = generate_hypotheses(notes, max_hypotheses=3)
    assert len(hyps) <= 3


def test_filter_testable():
    hyps = [
        Hypothesis("H1", testable=True),
        Hypothesis("H2", testable=False),
        Hypothesis("H3", testable=True),
    ]
    result = filter_testable(hyps)
    assert len(result) == 2


def test_rank_by_confidence():
    hyps = [
        Hypothesis("H1", confidence=0.4),
        Hypothesis("H2", confidence=0.9),
        Hypothesis("H3", confidence=0.6),
    ]
    ranked = rank_by_confidence(hyps)
    assert ranked[0].confidence == 0.9


def test_to_dict():
    h = Hypothesis("AI improves productivity.", basis=["note1"], confidence=0.7)
    d = h.to_dict()
    assert d["confidence"] == 0.7 and d["testable"] is True
