from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass
class EnrichedDocument:
    doc_id: str
    original_metadata: dict[str, Any]
    enriched_metadata: dict[str, Any]

    def merged(self) -> dict[str, Any]:
        return {**self.original_metadata, **self.enriched_metadata}

    def to_dict(self) -> dict:
        return {
            "doc_id": self.doc_id,
            "original": self.original_metadata,
            "enriched": self.enriched_metadata,
        }


_YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
_DOI_RE = re.compile(r"\b10\.\d{4,}/\S+\b")


def extract_year(text: str) -> int | None:
    m = _YEAR_RE.search(text)
    return int(m.group(0)) if m else None


def extract_doi(text: str) -> str | None:
    m = _DOI_RE.search(text)
    return m.group(0) if m else None


def infer_domain(url: str) -> str:
    try:
        return urlparse(url).netloc or ""
    except Exception:
        return ""


def infer_content_type(text: str) -> str:
    text_lower = text.lower()
    if "abstract" in text_lower and "doi" in text_lower:
        return "academic_paper"
    if text_lower.startswith("#") or "##" in text:
        return "markdown_doc"
    if "<html" in text_lower:
        return "html_page"
    return "plain_text"


def enrich_document(
    doc_id: str,
    text: str,
    original_metadata: dict[str, Any] | None = None,
    url: str = "",
) -> EnrichedDocument:
    meta = original_metadata or {}
    enriched: dict[str, Any] = {}

    year = extract_year(text)
    if year:
        enriched["year"] = year

    doi = extract_doi(text)
    if doi:
        enriched["doi"] = doi

    if url:
        enriched["domain"] = infer_domain(url)

    enriched["content_type"] = infer_content_type(text)
    enriched["char_count"] = len(text)
    enriched["word_count"] = len(text.split())

    return EnrichedDocument(
        doc_id=doc_id,
        original_metadata=meta,
        enriched_metadata=enriched,
    )


def enrich_batch(
    documents: list[dict],
) -> list[EnrichedDocument]:
    results = []
    for doc in documents:
        results.append(enrich_document(
            doc_id=doc.get("id", ""),
            text=doc.get("text", ""),
            original_metadata=doc.get("metadata"),
            url=doc.get("url", ""),
        ))
    return results
