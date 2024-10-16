"""Cross-encoder reranker for retrieved documents."""
from __future__ import annotations

import logging
from typing import Any

from langchain_core.documents import Document

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:
    """Reranks retrieved documents using a sentence-transformers cross-encoder.

    The cross-encoder model is lazy-loaded on first use so that importing this
    module does not trigger a heavyweight model download.

    The model ``cross-encoder/ms-marco-MiniLM-L-6-v2`` is a well-known,
    relatively small (22 M parameters) passage reranking model trained on the
    MS MARCO dataset.  It scores (query, passage) pairs directly instead of
    comparing separate embeddings, which makes it more accurate than bi-encoder
    cosine similarity for reranking.

    Example
    -------
    >>> reranker = CrossEncoderReranker()
    >>> docs = retriever.get_relevant_documents("What is RAG?")
    >>> reranked = reranker.rerank("What is RAG?", docs, top_k=4)
    """

    def __init__(self, model_name: str = _DEFAULT_MODEL) -> None:
        """
        Parameters
        ----------
        model_name:
            HuggingFace model ID for the cross-encoder.  Defaults to
            ``cross-encoder/ms-marco-MiniLM-L-6-v2``.
        """
        self._model_name = model_name
        self._model: Any | None = None  # loaded lazily

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rerank(
        self,
        query: str,
        docs: list[Document],
        top_k: int = 4,
    ) -> list[Document]:
        """Rerank *docs* by cross-encoder relevance score and return top-*top_k*.

        Parameters
        ----------
        query:
            The search query to score each document against.
        docs:
            Candidate documents to rerank.
        top_k:
            Maximum number of documents to return.

        Returns
        -------
        list[Document]
            Documents sorted descending by cross-encoder score, capped at *top_k*.
            Each returned document has a ``rerank_score`` key added to its
            metadata so callers can inspect the raw score.
        """
        if not docs:
            return []

        model = self._load_model()
        pairs = [(query, doc.page_content) for doc in docs]

        try:
            scores: list[float] = model.predict(pairs).tolist()
        except Exception:
            logger.exception("CrossEncoder.predict failed — returning docs unsorted")
            return docs[:top_k]

        scored = sorted(
            zip(docs, scores),
            key=lambda x: x[1],
            reverse=True,
        )

        results: list[Document] = []
        for doc, score in scored[:top_k]:
            # Attach the score to metadata so it is visible to downstream nodes.
            enriched = Document(
                page_content=doc.page_content,
                metadata={**doc.metadata, "rerank_score": round(score, 6)},
            )
            results.append(enriched)

        logger.debug(
            "Reranked %d docs → top %d (best score=%.4f)",
            len(docs),
            len(results),
            results[0].metadata["rerank_score"] if results else 0.0,
        )
        return results

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_model(self) -> Any:
        """Lazy-load the cross-encoder model on first call.

        Raises
        ------
        ImportError
            If ``sentence-transformers`` is not installed.
        """
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder  # type: ignore[import-untyped]
            except ImportError as exc:
                raise ImportError(
                    "sentence-transformers is required for reranking. "
                    "Install it with: pip install sentence-transformers"
                ) from exc

            logger.info("Loading cross-encoder model: %s", self._model_name)
            self._model = CrossEncoder(self._model_name)
            logger.info("Cross-encoder model loaded")

        return self._model
