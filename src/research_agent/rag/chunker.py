"""Advanced chunking strategies beyond simple recursive splitting."""

from __future__ import annotations

import logging
import re
from typing import Any

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def _copy_metadata(source: Document, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    meta = dict(source.metadata)
    if extra:
        meta.update(extra)
    return meta


class AdvancedChunker:
    """Multiple chunking strategies for LangChain Documents.

    All methods preserve all metadata from source documents and add a
    ``chunk_index`` and ``chunk_strategy`` key to each output Document's
    metadata.

    Example
    -------
    >>> chunker = AdvancedChunker()
    >>> chunks = chunker.sentence_chunk(docs, sentences_per_chunk=5)
    >>> chunks = chunker.sliding_window_chunk(docs, size=800, step=400)
    """

    # ------------------------------------------------------------------
    # Semantic chunking
    # ------------------------------------------------------------------

    def semantic_chunk(
        self,
        docs: list[Document],
        min_size: int = 200,
        max_size: int = 1000,
    ) -> list[Document]:
        """Split documents at semantic boundaries (paragraphs, headers, lists).

        Identifies natural breakpoints — blank lines, Markdown headers,
        bullet-list boundaries — and splits there.  Small fragments are merged
        into their neighbours until they reach *min_size*.  Fragments that
        exceed *max_size* are hard-split at the nearest sentence boundary.

        Parameters
        ----------
        docs:
            Source documents to chunk.
        min_size:
            Minimum character length for a chunk (before merging adjacent
            small fragments).
        max_size:
            Maximum character length for a chunk (will be hard-split if over).

        Returns
        -------
        list[Document]
            Semantically-bounded chunks with preserved metadata.
        """
        chunks: list[Document] = []
        chunk_index = 0

        for doc in docs:
            raw_sections = self._split_at_semantic_boundaries(doc.page_content)
            merged = self._merge_small_sections(raw_sections, min_size)

            for section in merged:
                if len(section) > max_size:
                    # Hard-split oversized sections at sentence boundaries
                    sub_sections = self._hard_split(section, max_size)
                else:
                    sub_sections = [section]

                for sub in sub_sections:
                    text = sub.strip()
                    if not text:
                        continue
                    chunks.append(
                        Document(
                            page_content=text,
                            metadata=_copy_metadata(
                                doc,
                                {
                                    "chunk_index": chunk_index,
                                    "chunk_strategy": "semantic",
                                },
                            ),
                        )
                    )
                    chunk_index += 1

        logger.debug(
            "semantic_chunk: %d docs → %d chunks (min=%d, max=%d)",
            len(docs),
            len(chunks),
            min_size,
            max_size,
        )
        return chunks

    # ------------------------------------------------------------------
    # Sliding window chunking
    # ------------------------------------------------------------------

    def sliding_window_chunk(
        self,
        docs: list[Document],
        size: int = 800,
        step: int = 400,
    ) -> list[Document]:
        """Create overlapping chunks using a sliding window over characters.

        Parameters
        ----------
        docs:
            Source documents.
        size:
            Window size in characters.
        step:
            Number of characters to advance the window per step.  A step
            smaller than *size* creates overlap between consecutive chunks.

        Returns
        -------
        list[Document]
            Overlapping chunks with ``window_start`` / ``window_end`` in metadata.
        """
        if step <= 0 or size <= 0:
            raise ValueError(f"size and step must be positive; got size={size}, step={step}")

        chunks: list[Document] = []
        chunk_index = 0

        for doc in docs:
            text = doc.page_content
            start = 0
            while start < len(text):
                end = min(start + size, len(text))
                window_text = text[start:end].strip()
                if window_text:
                    chunks.append(
                        Document(
                            page_content=window_text,
                            metadata=_copy_metadata(
                                doc,
                                {
                                    "chunk_index": chunk_index,
                                    "chunk_strategy": "sliding_window",
                                    "window_start": start,
                                    "window_end": end,
                                },
                            ),
                        )
                    )
                    chunk_index += 1
                start += step

        logger.debug(
            "sliding_window_chunk: %d docs → %d chunks (size=%d, step=%d)",
            len(docs),
            len(chunks),
            size,
            step,
        )
        return chunks

    # ------------------------------------------------------------------
    # Sentence-aware chunking
    # ------------------------------------------------------------------

    def sentence_chunk(
        self,
        docs: list[Document],
        sentences_per_chunk: int = 5,
    ) -> list[Document]:
        """Group documents into chunks of exactly *sentences_per_chunk* sentences.

        Sentences are detected with a simple regex that handles abbreviations
        reasonably well.  When ``nltk`` is available its tokeniser is used
        instead for better accuracy.

        Parameters
        ----------
        docs:
            Source documents.
        sentences_per_chunk:
            How many sentences to include in each chunk.

        Returns
        -------
        list[Document]
            Sentence-bounded chunks.
        """
        chunks: list[Document] = []
        chunk_index = 0

        for doc in docs:
            sentences = self._split_sentences(doc.page_content)
            for i in range(0, len(sentences), sentences_per_chunk):
                group = sentences[i : i + sentences_per_chunk]
                text = " ".join(group).strip()
                if not text:
                    continue
                chunks.append(
                    Document(
                        page_content=text,
                        metadata=_copy_metadata(
                            doc,
                            {
                                "chunk_index": chunk_index,
                                "chunk_strategy": "sentence",
                                "sentence_start": i,
                                "sentence_end": i + len(group),
                            },
                        ),
                    )
                )
                chunk_index += 1

        logger.debug(
            "sentence_chunk: %d docs → %d chunks (%d sentences/chunk)",
            len(docs),
            len(chunks),
            sentences_per_chunk,
        )
        return chunks

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _split_at_semantic_boundaries(text: str) -> list[str]:
        """Split *text* at paragraph/header/list boundaries."""
        # Split on: blank lines (paragraphs), Markdown headers, horizontal rules.
        # Keep the delimiter in the following section so headers stay with their content.
        sections = re.split(r"(\n\s*\n|\n#{1,6} |\n---+\n|\n\*\*\*+\n)", text)
        result: list[str] = []
        i = 0
        while i < len(sections):
            if i + 1 < len(sections) and re.match(r"\n#{1,6} ", sections[i + 1]):
                # Merge delimiter into next section (keep header with content)
                merged = sections[i] + sections[i + 1]
                i += 2
                if i < len(sections):
                    merged += sections[i]
                    i += 1
                result.append(merged)
            else:
                result.append(sections[i])
                i += 1
        return [s for s in result if s.strip()]

    @staticmethod
    def _merge_small_sections(sections: list[str], min_size: int) -> list[str]:
        """Merge adjacent sections until they meet *min_size*."""
        merged: list[str] = []
        buffer = ""
        for section in sections:
            buffer = (buffer + "\n\n" + section).strip() if buffer else section
            if len(buffer) >= min_size:
                merged.append(buffer)
                buffer = ""
        if buffer:
            if merged:
                merged[-1] = merged[-1] + "\n\n" + buffer
            else:
                merged.append(buffer)
        return merged

    @staticmethod
    def _hard_split(text: str, max_size: int) -> list[str]:
        """Split *text* into pieces no longer than *max_size* at sentence boundaries."""
        # Try to split at sentence ends first.
        sentence_re = re.compile(r"(?<=[.!?])\s+")
        sentences = sentence_re.split(text)
        parts: list[str] = []
        current = ""
        for sent in sentences:
            candidate = (current + " " + sent).strip() if current else sent
            if len(candidate) > max_size and current:
                parts.append(current)
                current = sent
            else:
                current = candidate
        if current:
            parts.append(current)
        return parts or [text]

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """Split *text* into individual sentences.

        Uses ``nltk.sent_tokenize`` when available, falls back to regex.
        """
        try:
            import nltk  # type: ignore[import-untyped]

            try:
                return nltk.sent_tokenize(text)
            except LookupError:
                nltk.download("punkt", quiet=True)
                return nltk.sent_tokenize(text)
        except ImportError:
            pass

        # Regex fallback — handles common abbreviations minimally.
        pattern = re.compile(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s")
        return [s.strip() for s in pattern.split(text) if s.strip()]
