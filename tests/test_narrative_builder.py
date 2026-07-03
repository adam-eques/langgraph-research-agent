from __future__ import annotations

from research_agent.agents.narrative_builder import (
    NarrativeSegment,
    add_transition,
    build_narrative,
    render_narrative,
)


def test_build_narrative_basic():
    frags = [
        {"text": "AI is advancing rapidly.", "type": "finding"},
        {"text": "Data quality remains an issue.", "type": "limitation"},
    ]
    segments = build_narrative(frags, topic="AI progress")
    assert len(segments) >= 3
    assert segments[0].segment_type == "intro"


def test_build_narrative_empty():
    assert build_narrative([]) == []


def test_render_narrative():
    segments = [
        NarrativeSegment("First sentence.", "finding", 0),
        NarrativeSegment("Second sentence.", "implication", 1),
    ]
    text = render_narrative(segments)
    assert "First sentence." in text and "Second sentence." in text


def test_conclusion_appended():
    frags = [{"text": "Fact one.", "type": "finding"}]
    segments = build_narrative(frags)
    last = max(segments, key=lambda s: s.order)
    assert last.segment_type == "conclusion"


def test_transition_finding_to_limitation():
    t = add_transition("finding", "limitation")
    assert "However" in t


def test_narrative_segment_to_dict():
    s = NarrativeSegment("content", "finding", 2)
    d = s.to_dict()
    assert d["order"] == 2 and d["type"] == "finding"
