from __future__ import annotations

from research_agent.agents.outline_generator import (
    OutlineSection,
    generate_outline,
    outline_to_markdown,
)


def test_generate_outline_returns_sections():
    sections = generate_outline("AI", ["Machine Learning", "Deep Learning"])
    assert len(sections) == 2 and sections[0].title == "Machine Learning"


def test_subsections_depth2():
    sections = generate_outline("AI", ["neural networks"], depth=2)
    assert len(sections[0].subsections) > 0


def test_outline_to_markdown_includes_topic():
    sections = [OutlineSection("Intro", level=1)]
    md = outline_to_markdown(sections, topic="AI Research")
    assert "# AI Research" in md and "## Intro" in md


def test_to_dict_structure():
    s = OutlineSection("Introduction", 1)
    d = s.to_dict()
    assert d["title"] == "Introduction" and "subsections" in d
