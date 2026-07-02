from __future__ import annotations

from research_agent.document_ranker import bm25_score, idf, rank_documents, tf


def test_tf_basic():
    assert tf("python", "python python java") > tf("java", "python python java")


def test_idf_decreases_with_frequency():
    docs = ["python is great", "python is popular", "java is different"]
    assert idf("python", docs) < idf("java", docs)


def test_bm25_scores_relevant_higher():
    docs_text = ["python machine learning", "cooking recipes", "java spring"]
    query = "python"
    score_0 = bm25_score(query, docs_text[0], docs_text)
    score_1 = bm25_score(query, docs_text[1], docs_text)
    assert score_0 > score_1


def test_rank_documents_order():
    docs = [
        {"content": "cooking recipes"},
        {"content": "python machine learning python"},
    ]
    ranked = rank_documents("python", docs)
    assert "python" in ranked[0]["content"]
