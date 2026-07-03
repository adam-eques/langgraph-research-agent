from __future__ import annotations

from research_agent.agents.abstract_generator import (
    extract_contributions,
    format_abstract,
    generate_abstract,
)


def test_generate_abstract_includes_title():
    result = generate_abstract(
        "LangGraph workflows", ["This system handles stateful multi-agent pipelines."]
    )
    assert "langgraph" in result.lower()


def test_generate_abstract_truncates():
    sections = ["Long section. " * 100]
    result = generate_abstract("AI", sections, max_chars=100)
    assert len(result) <= 150


def test_extract_contributions():
    text = "We propose a new approach to retrieval. This paper presents a novel framework."
    contribs = extract_contributions(text)
    assert len(contribs) >= 1


def test_format_abstract():
    d = format_abstract("AI research is growing.", ["new method"])
    assert "abstract" in d and "word_count" in d
