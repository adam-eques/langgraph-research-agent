from __future__ import annotations

import pytest
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from research_agent.context_builder import build_context_window, summarize_notes, estimate_tokens


def test_estimate_tokens_basic():
    assert estimate_tokens("hello world") > 0


def test_estimate_tokens_empty():
    assert estimate_tokens("") == 1


def test_build_context_window_keeps_recent():
    msgs = [HumanMessage(content=f"msg {i}") for i in range(20)]
    result = build_context_window(msgs, max_tokens=200)
    # Should keep most recent messages, not all 20
    assert len(result) <= 20


def test_build_context_window_preserves_system():
    msgs = [SystemMessage(content="system"), HumanMessage(content="user")]
    result = build_context_window(msgs, max_tokens=500)
    assert any(isinstance(m, SystemMessage) for m in result)


def test_summarize_notes_short():
    notes = ["Note A", "Note B"]
    result = summarize_notes(notes, max_chars=1000)
    assert "Note A" in result
    assert "Note B" in result


def test_summarize_notes_truncates():
    notes = ["x" * 1000] * 10
    result = summarize_notes(notes, max_chars=500)
    assert len(result) <= 530  # some buffer for truncation marker
