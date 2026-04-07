from __future__ import annotations

from research_agent.content_deduplicator import deduplicate_by_content, deduplicate_documents


def test_deduplicate_strings():
    items = ["Hello world", "Hello world", "Different content"]
    result = deduplicate_by_content(items)
    assert len(result) == 2


def test_deduplicate_preserves_order():
    items = ["first", "second", "first"]
    result = deduplicate_by_content(items)
    assert result[0] == "first"


def test_deduplicate_documents():
    docs = [
        {"page_content": "same content"},
        {"page_content": "same content"},
        {"page_content": "different content"},
    ]
    result = deduplicate_documents(docs)
    assert len(result) == 2


def test_deduplicate_empty():
    assert deduplicate_by_content([]) == []
