from __future__ import annotations

from research_agent.result_formatter import format_research_result


def test_markdown_output():
    result = format_research_result("AI?", "AI is...", [], [])
    assert "## Research" in result
    assert "AI is..." in result


def test_json_output():
    import json
    result = format_research_result("q", "a", [{"source": "x"}], [], style="json")
    data = json.loads(result)
    assert data["query"] == "q"
    assert data["citations"][0]["source"] == "x"


def test_plain_output():
    result = format_research_result("q", "answer", [{"source": "y"}], [], style="plain")
    assert "Query: q" in result
    assert "y" in result


def test_markdown_with_citations():
    result = format_research_result("q", "a", [{"source": "arxiv.org"}], [])
    assert "arxiv.org" in result
    assert "### Sources" in result
