from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def normalize_source(source: str) -> str:
    source = re.sub(r"https?://", "", source)
    source = source.rstrip("/")
    source = source.lower()
    return source


def deduplicate_citations(citations: list[dict]) -> list[dict]:
    seen, unique = set(), []
    for c in citations:
        source = normalize_source(c.get("source", ""))
        if source not in seen:
            seen.add(source)
            unique.append(c)
        else:
            logger.debug("Duplicate citation removed: %s", source)
    return unique


def merge_citation_lists(*lists: list[dict]) -> list[dict]:
    combined = [c for lst in lists for c in lst]
    return deduplicate_citations(combined)
