from __future__ import annotations

from research_agent.adaptive_chunker import AdaptiveChunker


def test_detect_prose():
    chunker = AdaptiveChunker()
    assert chunker.detect_content_type("This is plain text.") == "prose"


def test_detect_code():
    chunker = AdaptiveChunker()
    assert chunker.detect_content_type("def foo():\n    return 1") == "code"


def test_detect_table():
    chunker = AdaptiveChunker()
    assert chunker.detect_content_type("| A | B | C |") == "table"


def test_chunk_single_chunk():
    chunker = AdaptiveChunker(base_size=1000)
    result = chunker.chunk("short text")
    assert result == ["short text"]


def test_chunk_multiple_chunks():
    chunker = AdaptiveChunker(base_size=10, overlap=2)
    result = chunker.chunk("a" * 30)
    assert len(result) > 1
