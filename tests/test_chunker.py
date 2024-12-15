from __future__ import annotations

import pytest
from langchain_core.documents import Document

from research_agent.rag.chunker import AdvancedChunker


@pytest.fixture
def chunker():
    return AdvancedChunker()


@pytest.fixture
def sample_docs():
    long_text = "This is a sentence. " * 100
    return [Document(page_content=long_text, metadata={"source": "test.txt"})]


def test_semantic_chunk_splits(chunker, sample_docs):
    chunks = chunker.semantic_chunk(sample_docs, min_size=50, max_size=300)
    assert len(chunks) > 1


def test_semantic_chunk_preserves_metadata(chunker, sample_docs):
    chunks = chunker.semantic_chunk(sample_docs)
    assert all(c.metadata.get("source") == "test.txt" for c in chunks)


def test_sliding_window_chunk_splits(chunker, sample_docs):
    chunks = chunker.sliding_window_chunk(sample_docs, size=200, step=100)
    assert len(chunks) > 1


def test_sliding_window_chunk_overlap(chunker):
    text = " ".join(f"word{i}" for i in range(100))
    docs = [Document(page_content=text, metadata={})]
    chunks = chunker.sliding_window_chunk(docs, size=50, step=25)
    # With overlap, adjacent chunks should share some content
    assert len(chunks) > 2


def test_sentence_chunk_splits(chunker):
    text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence. Sixth sentence."
    docs = [Document(page_content=text, metadata={"source": "s.txt"})]
    chunks = chunker.sentence_chunk(docs, sentences_per_chunk=2)
    assert len(chunks) >= 2


def test_sentence_chunk_preserves_metadata(chunker, sample_docs):
    chunks = chunker.sentence_chunk(sample_docs, sentences_per_chunk=5)
    assert all(c.metadata.get("source") == "test.txt" for c in chunks)


def test_empty_docs_return_empty(chunker):
    assert chunker.semantic_chunk([]) == []
    assert chunker.sliding_window_chunk([]) == []
    assert chunker.sentence_chunk([]) == []
