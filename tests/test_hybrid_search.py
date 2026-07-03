"""Tests for BM25 indexing and hybrid search RRF merging."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from langchain_core.documents import Document

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_docs(contents: list[str]) -> list[Document]:
    return [
        Document(page_content=c, metadata={"source": f"doc{i}"}) for i, c in enumerate(contents)
    ]


# ---------------------------------------------------------------------------
# index_for_bm25
# ---------------------------------------------------------------------------


class TestIndexForBm25:
    def test_returns_bm25_okapi_instance(self):
        pytest.importorskip("rank_bm25")
        from rank_bm25 import BM25Okapi

        from research_agent.rag.hybrid_search import index_for_bm25

        docs = _make_docs(["the quick brown fox", "a slow lazy dog"])
        index = index_for_bm25(docs)

        assert isinstance(index, BM25Okapi)

    def test_scores_relevant_doc_higher(self):
        pytest.importorskip("rank_bm25")
        from research_agent.rag.hybrid_search import index_for_bm25

        docs = _make_docs(
            [
                "neural networks and deep learning",
                "recipes for banana bread baking",
            ]
        )
        index = index_for_bm25(docs)
        scores = index.get_scores(["neural", "networks"])

        assert scores[0] > scores[1]

    def test_empty_docs(self):
        pytest.importorskip("rank_bm25")
        from research_agent.rag.hybrid_search import index_for_bm25

        index = index_for_bm25([])
        # Should not raise; BM25 with 0 docs returns zero scores
        assert index is not None

    def test_raises_without_rank_bm25(self, monkeypatch):
        import sys

        monkeypatch.setitem(sys.modules, "rank_bm25", None)

        import importlib

        import research_agent.rag.hybrid_search as hs

        importlib.reload(hs)

        # After reload the import inside the function should raise ImportError
        with pytest.raises(ImportError, match="rank_bm25"):
            hs.index_for_bm25(_make_docs(["test"]))


# ---------------------------------------------------------------------------
# RRF fusion (_reciprocal_rank_fusion is private but testable directly)
# ---------------------------------------------------------------------------


class TestReciprocalRankFusion:
    def test_combines_two_lists(self):
        from research_agent.rag.hybrid_search import _reciprocal_rank_fusion

        # List A ranks doc 0 first; List B ranks doc 2 first.
        result = _reciprocal_rank_fusion([[0, 1, 2], [2, 0, 1]])
        indices = [idx for idx, _ in result]

        # Doc 0 appears at position 0 in A and position 1 in B → strong rank
        # Doc 2 appears at position 2 in A and position 0 in B
        assert 0 in indices
        assert 2 in indices

    def test_single_list_preserves_order(self):
        from research_agent.rag.hybrid_search import _reciprocal_rank_fusion

        result = _reciprocal_rank_fusion([[3, 1, 2]])
        indices = [idx for idx, _ in result]
        assert indices == [3, 1, 2]

    def test_scores_are_positive(self):
        from research_agent.rag.hybrid_search import _reciprocal_rank_fusion

        result = _reciprocal_rank_fusion([[0, 1], [1, 0]])
        for _, score in result:
            assert score > 0

    def test_empty_lists(self):
        from research_agent.rag.hybrid_search import _reciprocal_rank_fusion

        assert _reciprocal_rank_fusion([]) == []
        assert _reciprocal_rank_fusion([[]]) == []


# ---------------------------------------------------------------------------
# HybridSearcher
# ---------------------------------------------------------------------------


class TestHybridSearcher:
    def _make_searcher(self, semantic_docs: list[Document] | None = None):
        mock_store = MagicMock()
        mock_store.similarity_search.return_value = semantic_docs or []
        from research_agent.rag.hybrid_search import HybridSearcher

        return HybridSearcher(vector_store=mock_store)

    def test_returns_at_most_k_results(self):
        pytest.importorskip("rank_bm25")
        docs = _make_docs([f"document about topic {i}" for i in range(10)])
        searcher = self._make_searcher(semantic_docs=docs[:5])

        results = searcher.search("topic", docs, k=4)
        assert len(results) <= 4

    def test_returns_empty_for_empty_docs(self):
        searcher = self._make_searcher()
        results = searcher.search("query", [], k=4)
        assert results == []

    def test_returns_document_objects(self):
        pytest.importorskip("rank_bm25")
        docs = _make_docs(["machine learning fundamentals", "cooking pasta at home"])
        searcher = self._make_searcher(semantic_docs=docs[:1])

        results = searcher.search("machine learning", docs, k=2)
        for r in results:
            assert isinstance(r, Document)
            assert r.page_content

    def test_deduplicates_results(self):
        pytest.importorskip("rank_bm25")
        docs = _make_docs(["alpha beta gamma", "delta epsilon zeta"])
        # Both BM25 and semantic return the same doc
        searcher = self._make_searcher(semantic_docs=[docs[0]])

        results = searcher.search("alpha", docs, k=2)
        contents = [r.page_content for r in results]
        assert len(contents) == len(set(contents))  # no duplicates
