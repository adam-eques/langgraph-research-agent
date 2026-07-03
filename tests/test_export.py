from __future__ import annotations

import json

import pytest

from research_agent.export import ReportExporter


@pytest.fixture
def sample_result():
    return {
        "query": "What is LangGraph?",
        "answer": "LangGraph is a library for building stateful multi-agent applications.",
        "research_notes": ["Key finding: LangGraph uses StateGraph for workflow definition."],
        "citations": [
            {"source": "langchain_docs.pdf", "excerpt": "LangGraph...", "relevance": "high"}
        ],
    }


def test_to_markdown_contains_answer(sample_result):
    md = ReportExporter.to_markdown(sample_result)
    assert "LangGraph is a library" in md


def test_to_markdown_contains_query(sample_result):
    md = ReportExporter.to_markdown(sample_result)
    assert "What is LangGraph?" in md


def test_to_markdown_contains_citations(sample_result):
    md = ReportExporter.to_markdown(sample_result)
    assert "langchain_docs.pdf" in md


def test_to_html_has_html_tags(sample_result):
    html = ReportExporter.to_html(sample_result)
    assert "<html" in html or "<!DOCTYPE" in html or "<body" in html


def test_to_json_valid_json(sample_result):
    raw = ReportExporter.to_json(sample_result)
    parsed = json.loads(raw)
    assert parsed["query"] == sample_result["query"]
    assert parsed["answer"] == sample_result["answer"]


def test_to_json_includes_all_keys(sample_result):
    raw = ReportExporter.to_json(sample_result)
    parsed = json.loads(raw)
    for key in ("query", "answer", "research_notes", "citations"):
        assert key in parsed
