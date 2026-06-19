from __future__ import annotations
from research_agent.agents.gap_analyzer import (
    ResearchGap,
    detect_uncertainty,
    find_gaps,
    prioritize_gaps,
)


def test_detect_uncertainty_basic():
    text = "This phenomenon is not yet understood and further research is needed."
    matches = detect_uncertainty(text)
    assert len(matches) >= 2


def test_detect_uncertainty_no_match():
    text = "We have a clear understanding of this mechanism."
    assert detect_uncertainty(text) == []


def test_find_gaps_from_notes():
    notes = [
        "The cause of this disease remains unclear and little is known about its mechanism.",
        "Conventional treatments are well documented.",
    ]
    gaps = find_gaps(notes)
    assert len(gaps) >= 1
    assert any("unclear" in g.description.lower() or "known" in g.description.lower() for g in gaps)


def test_find_gaps_required_topics():
    notes = ["AI is transforming industries rapidly."]
    gaps = find_gaps(notes, required_topics=["quantum computing"])
    assert any("quantum computing" in g.topic.lower() for g in gaps)


def test_prioritize_gaps():
    gaps = [
        ResearchGap("T1", "desc", priority="low"),
        ResearchGap("T2", "desc", priority="high"),
        ResearchGap("T3", "desc", priority="medium"),
    ]
    ranked = prioritize_gaps(gaps)
    assert ranked[0].priority == "high"


def test_gap_to_dict():
    g = ResearchGap("Topic", "Unclear.", priority="high", suggested_queries=["q1"])
    d = g.to_dict()
    assert d["priority"] == "high" and "suggested_queries" in d
