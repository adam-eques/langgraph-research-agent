from __future__ import annotations
from research_agent.rag.hybrid_retriever import (
    RetrievedDoc, reciprocal_rank_fusion, HybridRetriever,
)


def _doc(text: str, score: float = 1.0) -> RetrievedDoc:
    return RetrievedDoc(content=text, score=score)


def test_rrf_combines_results():
    dense = [_doc("doc A"), _doc("doc B")]
    sparse = [_doc("doc B"), _doc("doc C")]
    merged = reciprocal_rank_fusion(dense, sparse)
    texts = [d.content for d in merged]
    assert "doc B" in texts[0]


def test_rrf_all_unique():
    dense = [_doc("X"), _doc("Y")]
    sparse = [_doc("Z"), _doc("W")]
    merged = reciprocal_rank_fusion(dense, sparse)
    assert len(merged) == 4


def test_hybrid_retriever_top_k():
    hr = HybridRetriever()
    dense = [_doc(f"dense{i}") for i in range(5)]
    sparse = [_doc(f"sparse{i}") for i in range(5)]
    results = hr.retrieve(dense, sparse, top_k=3)
    assert len(results) == 3


def test_retrieved_doc_defaults():
    d = RetrievedDoc(content="hello", score=0.5)
    assert d.metadata == {} and d.source == ""
