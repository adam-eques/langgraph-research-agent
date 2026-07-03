from __future__ import annotations

from research_agent.rag.reranker import cross_encoder_score, rerank


def test_cross_encoder_score_relevant():
    score = cross_encoder_score("python machine learning", "python is used for machine learning")
    assert score > 0.3


def test_rerank_orders_by_relevance():
    docs = [
        {"content": "cooking and recipes for dinner", "score": 0.9},
        {"content": "python machine learning frameworks", "score": 0.5},
    ]
    ranked = rerank("python machine learning", docs)
    assert "python" in ranked[0].content


def test_rerank_respects_top_k():
    docs = [{"content": f"doc {i}", "score": 0.5} for i in range(10)]
    ranked = rerank("test", docs, top_k=3)
    assert len(ranked) == 3


def test_final_score_range():
    docs = [{"content": "text", "score": 0.5}]
    ranked = rerank("text", docs)
    assert 0.0 <= ranked[0].final_score <= 1.0
