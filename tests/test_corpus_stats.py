from __future__ import annotations
from research_agent.rag.corpus_stats import CorpusStats, tokenize


def test_tokenize():
    tokens = tokenize("Hello World, this is a TEST.")
    assert "hello" in tokens and "world" in tokens


def test_add_document_updates_df():
    stats = CorpusStats()
    stats.add_document("machine learning is powerful")
    assert stats.df("machine") == 1


def test_idf_zero_for_missing_term():
    stats = CorpusStats()
    stats.add_document("hello world")
    assert stats.idf("nonexistent") == 0.0


def test_idf_lower_for_common_term():
    stats = CorpusStats()
    for _ in range(10):
        stats.add_document("the quick brown fox")
    stats.add_document("unique rare term exists here")
    idf_common = stats.idf("the")
    idf_rare = stats.idf("unique")
    assert idf_rare > idf_common


def test_tf_basic():
    stats = CorpusStats()
    stats.add_document("ai ai ai is great")
    assert stats.tf("ai", 0) > 0.0


def test_tfidf():
    stats = CorpusStats()
    stats.add_document("deep learning neural networks")
    assert stats.tfidf("deep", 0) > 0


def test_top_terms():
    stats = CorpusStats()
    stats.add_document("research paper citation analysis")
    stats.add_document("paper citation bibliography")
    top = stats.top_terms(n=3)
    assert len(top) <= 3
