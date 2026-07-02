"""Hybrid BM25 + semantic search with Reciprocal Rank Fusion (RRF)."""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# RRF constant — 60 is the standard value from the original paper.
_RRF_K = 60


def index_for_bm25(docs: list[Document]) -> Any:  # returns BM25Okapi
    """Build a BM25Okapi index from a list of LangChain Documents.

    Parameters
    ----------
    docs:
        Documents whose ``page_content`` will be tokenised and indexed.

    Returns
    -------
    BM25Okapi
        A fitted rank_bm25 index ready for scoring.

    Raises
    ------
    ImportError
        If ``rank_bm25`` is not installed.
    """
    try:
        from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "rank_bm25 is required for BM25 search. Install it with: pip install rank-bm25"
        ) from exc

    tokenised = [doc.page_content.lower().split() for doc in docs]
    if not tokenised:
        # BM25Okapi divides by the corpus size, so an empty corpus raises
        # ZeroDivisionError. Seed a single placeholder document instead.
        tokenised = [["__empty__"]]

    bm25 = BM25Okapi(tokenised)

    # On tiny corpora a term appearing in half the documents collapses to an
    # idf of 0, which makes every document score 0. Floor non-positive idf so
    # relevant documents still rank above irrelevant ones.
    for term, value in bm25.idf.items():
        if value <= 0:
            bm25.idf[term] = 0.5
    return bm25


def _reciprocal_rank_fusion(
    ranked_lists: list[list[int]],
    k: int = _RRF_K,
) -> list[tuple[int, float]]:
    """Combine multiple ranked lists of document indices using RRF.

    Parameters
    ----------
    ranked_lists:
        Each inner list is an ordered sequence of document indices (best first).
    k:
        RRF constant.  Higher values diminish the impact of top-ranked items.

    Returns
    -------
    list[tuple[int, float]]
        ``(doc_index, rrf_score)`` pairs sorted by descending score.
    """
    scores: dict[int, float] = defaultdict(float)
    for ranked in ranked_lists:
        for rank, doc_idx in enumerate(ranked):
            scores[doc_idx] += 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


class HybridSearcher:
    """Combines keyword (BM25) and semantic (vector) search with RRF merging.

    The BM25 index is built on-the-fly from the candidate documents passed to
    :meth:`search`.  The semantic search is performed via a Chroma vector store
    that must be provided at construction time or via the factory helper.

    Example
    -------
    >>> from langchain_chroma import Chroma
    >>> store = Chroma(...)
    >>> searcher = HybridSearcher(vector_store=store)
    >>> results = searcher.search("machine learning transformers", docs, k=4)
    """

    def __init__(self, vector_store: Any) -> None:
        """
        Parameters
        ----------
        vector_store:
            A LangChain vector store that exposes ``similarity_search(query, k)``.
        """
        self._vector_store = vector_store

    def search(
        self,
        query: str,
        docs: list[Document],
        k: int = 4,
        bm25_weight: float = 0.5,
        semantic_weight: float = 0.5,
    ) -> list[Document]:
        """Run hybrid BM25 + semantic search and return the top-*k* documents.

        Both searches produce a ranked list; the lists are merged with RRF and
        the top-*k* unique documents are returned.

        Parameters
        ----------
        query:
            The natural-language search query.
        docs:
            Candidate documents to search over (used for BM25 index construction).
        k:
            Number of results to return.
        bm25_weight:
            Relative weight for BM25 rankings in RRF (unused directly — RRF
            handles fusion implicitly; kept for future weighted-RRF extension).
        semantic_weight:
            Relative weight for semantic rankings (see ``bm25_weight``).

        Returns
        -------
        list[Document]
            Top-*k* documents ranked by fused RRF score.
        """
        if not docs:
            logger.warning("hybrid_search called with empty document list")
            return []

        # --- BM25 ranking ---
        bm25_ranked = self._bm25_rank(query, docs, top_n=min(len(docs), k * 3))

        # --- Semantic ranking ---
        semantic_ranked = self._semantic_rank(query, docs, top_n=min(len(docs), k * 3))

        # --- RRF fusion ---
        fused = _reciprocal_rank_fusion([bm25_ranked, semantic_ranked])

        # Deduplicate and materialise
        seen: set[int] = set()
        results: list[Document] = []
        for doc_idx, _score in fused:
            if doc_idx not in seen and doc_idx < len(docs):
                seen.add(doc_idx)
                results.append(docs[doc_idx])
                if len(results) >= k:
                    break

        logger.debug(
            "HybridSearch: bm25_candidates=%d, semantic_candidates=%d, returned=%d",
            len(bm25_ranked),
            len(semantic_ranked),
            len(results),
        )
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _bm25_rank(self, query: str, docs: list[Document], top_n: int) -> list[int]:
        """Return top-*top_n* document indices ranked by BM25 score."""
        try:
            bm25 = index_for_bm25(docs)
        except ImportError:
            logger.warning("rank_bm25 not available — skipping BM25 leg of hybrid search")
            return []

        tokenised_query = query.lower().split()
        scores = bm25.get_scores(tokenised_query)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return ranked[:top_n]

    def _semantic_rank(self, query: str, docs: list[Document], top_n: int) -> list[int]:
        """Return top-*top_n* document indices ranked by cosine similarity.

        The semantic search is done through the vector store.  We map the
        returned documents back to their index in *docs* by content hash so
        that the RRF fusion can work on indices.
        """
        try:
            semantic_docs = self._vector_store.similarity_search(query, k=top_n)
        except Exception:
            logger.exception("Semantic search failed — using empty semantic results")
            return []

        # Build a content-hash → index map for fast lookup
        content_to_idx: dict[str, int] = {doc.page_content: i for i, doc in enumerate(docs)}

        ranked: list[int] = []
        for sem_doc in semantic_docs:
            idx = content_to_idx.get(sem_doc.page_content)
            if idx is not None:
                ranked.append(idx)
        return ranked
