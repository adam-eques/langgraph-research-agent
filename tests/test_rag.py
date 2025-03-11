from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from research_agent.rag.ingestion import split_documents


def test_split_documents_chunks_correctly():
    long_text = "word " * 400
    doc = Document(page_content=long_text, metadata={"source": "test.txt"})
    chunks = split_documents([doc])
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 1200


def test_split_preserves_metadata():
    doc = Document(page_content="short content", metadata={"source": "test.txt", "filename": "test.txt"})
    chunks = split_documents([doc])
    assert all(c.metadata.get("source") == "test.txt" for c in chunks)


@patch("research_agent.rag.retriever._get_store")
def test_retrieve_returns_documents(mock_store):
    mock_chroma = MagicMock()
    mock_chroma.similarity_search.return_value = [
        Document(page_content="relevant passage", metadata={"filename": "report.pdf"})
    ]
    mock_store.return_value = mock_chroma

    from research_agent.rag.retriever import retrieve
    results = retrieve("test query", k=1)
    assert len(results) == 1
    assert results[0].page_content == "relevant passage"
