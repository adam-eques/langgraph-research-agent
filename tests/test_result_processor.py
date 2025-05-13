from __future__ import annotations
from research_agent.rag.result_processor import merge_retrieval_results, normalize_scores, top_k_by_score

def test_merge_deduplicates():
    a = [{"page_content": "doc A content here"}]
    b = [{"page_content": "doc A content here"}, {"page_content": "doc B"}]
    result = merge_retrieval_results(a, b)
    assert len(result) == 2

def test_normalize_scores():
    docs = [{"score": 0.2}, {"score": 0.8}]
    result = normalize_scores(docs)
    assert result[0]["score"] == 0.0
    assert result[1]["score"] == 1.0

def test_top_k():
    docs = [{"score": 0.1}, {"score": 0.9}, {"score": 0.5}]
    result = top_k_by_score(docs, k=2)
    assert result[0]["score"] == 0.9
