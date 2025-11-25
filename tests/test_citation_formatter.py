from __future__ import annotations

from research_agent.citation_formatter import format_apa, format_inline_citation, build_references_section


def test_format_apa_with_title_year():
    result = format_apa("https://arxiv.org/abs/123", title="AI Paper", year="2024")
    assert "AI Paper" in result
    assert "2024" in result
    assert "arxiv.org" in result


def test_format_apa_minimal():
    result = format_apa("https://openai.com")
    assert "openai.com" in result


def test_format_inline_citation():
    result = format_inline_citation(3, "https://arxiv.org/abs/123")
    assert result == "[3](arxiv.org)"


def test_build_references_section_empty():
    assert build_references_section([]) == ""


def test_build_references_section():
    citations = [{"source": "https://arxiv.org", "title": "Paper A", "year": "2023"}]
    result = build_references_section(citations)
    assert "## References" in result
    assert "Paper A" in result
