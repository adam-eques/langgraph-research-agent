from __future__ import annotations

import logging
import re
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def deduplicate(docs: list[Document], threshold: float = 0.9) -> list[Document]:
    """Remove near-duplicate documents based on content overlap."""
    seen: list[str] = []
    unique: list[Document] = []
    for doc in docs:
        content = doc.page_content.strip()
        is_dup = any(_overlap(content, s) >= threshold for s in seen)
        if not is_dup:
            seen.append(content)
            unique.append(doc)
    logger.debug("Deduplication: %d -> %d documents", len(docs), len(unique))
    return unique


def _overlap(a: str, b: str) -> float:
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def filter_by_score(docs: list[Document], min_score: float = 0.0) -> list[Document]:
    """Keep only documents whose rerank_score metadata meets the threshold."""
    filtered = [d for d in docs if float(d.metadata.get("rerank_score", 1.0)) >= min_score]
    logger.debug("Score filter (%.2f): %d -> %d", min_score, len(docs), len(filtered))
    return filtered


def sort_by_score(docs: list[Document]) -> list[Document]:
    """Sort documents descending by rerank_score metadata."""
    return sorted(docs, key=lambda d: float(d.metadata.get("rerank_score", 0.0)), reverse=True)


def strip_boilerplate(docs: list[Document]) -> list[Document]:
    """Remove common boilerplate patterns from document content."""
    patterns = [
        r"Page \d+ of \d+",
        r"CONFIDENTIAL",
        r"www\.\S+",
        r"\bCopyright\b.{0,60}",
    ]
    cleaned = []
    for doc in docs:
        content = doc.page_content
        for pat in patterns:
            content = re.sub(pat, "", content, flags=re.IGNORECASE)
        cleaned.append(Document(page_content=content.strip(), metadata=doc.metadata))
    return cleaned
