from __future__ import annotations
from research_agent.rag.sparse_retriever import SparseRetriever

def test_retrieve_returns_best_match():
    sr = SparseRetriever()
    sr.index(["machine learning tutorial", "sports news update", "deep learning guide"])
    results = sr.retrieve("machine learning", k=2)
    assert any("machine learning" in r[1] for r in results)

def test_retrieve_empty_index():
    sr = SparseRetriever()
    assert sr.retrieve("query") == []

def test_retrieve_no_match():
    sr = SparseRetriever()
    sr.index(["cat and dog", "sun and moon"])
    assert sr.retrieve("quantum physics") == []
