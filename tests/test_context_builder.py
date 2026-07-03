from __future__ import annotations

from research_agent.context_builder import build_context, build_messages, format_document


def test_format_document_with_source():
    doc = {"content": "Hello world", "source": "https://example.com"}
    result = format_document(doc, 0)
    assert "[1]" in result and "Hello world" in result


def test_build_context_basic():
    docs = [{"content": "doc content", "source": "src1"}]
    ctx = build_context(docs)
    assert "## Context" in ctx and "doc content" in ctx


def test_build_context_truncation():
    docs = [{"content": "x" * 5000}, {"content": "y" * 5000}]
    ctx = build_context(docs, max_chars=6000)
    assert "y" * 5000 not in ctx


def test_build_messages():
    msgs = build_messages("sys", "What is AI?", context="Some context")
    assert msgs[-1]["role"] == "user" and "What is AI?" in msgs[-1]["content"]


def test_build_messages_with_history():
    history = [{"role": "user", "content": "prev"}, {"role": "assistant", "content": "ans"}]
    msgs = build_messages("sys", "new", history=history)
    assert len(msgs) == 3
