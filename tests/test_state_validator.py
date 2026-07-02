from __future__ import annotations

import pytest

from research_agent.state_validator import assert_state_valid, validate_research_state


def test_valid_state():
    state = {
        "query": "what is AI?",
        "research_notes": ["note 1"],
        "citations": [{"source": "arxiv.org"}],
    }
    assert validate_research_state(state) == []


def test_missing_query():
    errors = validate_research_state({"query": "", "research_notes": [], "citations": []})
    assert any("query" in e for e in errors)


def test_invalid_notes_type():
    errors = validate_research_state(
        {"query": "q", "research_notes": "not a list", "citations": []}
    )
    assert any("research_notes" in e for e in errors)


def test_citation_missing_source():
    state = {"query": "q", "research_notes": [], "citations": [{"excerpt": "text"}]}
    errors = validate_research_state(state)
    assert any("source" in e for e in errors)


def test_assert_state_valid_raises():
    with pytest.raises(ValueError, match="Invalid ResearchState"):
        assert_state_valid({"query": "", "research_notes": [], "citations": []})
