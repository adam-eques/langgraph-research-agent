from __future__ import annotations

from research_agent.splitter import sentence_split, paragraph_split, token_aware_split


def test_sentence_split_basic():
    text = "Hello world. How are you? I am fine."
    result = sentence_split(text)
    assert len(result) == 3


def test_paragraph_split():
    text = "Para one.\n\nPara two.\n\nPara three."
    result = paragraph_split(text)
    assert len(result) == 3


def test_token_aware_split_short():
    result = token_aware_split("short text", max_tokens=1000)
    assert result == ["short text"]


def test_token_aware_split_long():
    text = ("This is a sentence. " * 100).strip()
    chunks = token_aware_split(text, max_tokens=50)
    assert len(chunks) > 1
    for c in chunks:
        assert len(c) <= 50 * 4 + 200
