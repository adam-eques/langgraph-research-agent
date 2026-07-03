from __future__ import annotations

import hashlib
import logging
import re

logger = logging.getLogger(__name__)


def _fingerprint(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())[:200]
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def deduplicate_by_content(items: list[str], similarity_chars: int = 200) -> list[str]:
    seen, unique = set(), []
    for item in items:
        fp = _fingerprint(item[:similarity_chars])
        if fp not in seen:
            seen.add(fp)
            unique.append(item)
        else:
            logger.debug("Duplicate content removed (fp=%s)", fp)
    return unique


def deduplicate_documents(docs: list[dict], content_key: str = "page_content") -> list[dict]:
    seen, unique = set(), []
    for doc in docs:
        content = doc.get(content_key, "")
        fp = _fingerprint(content)
        if fp not in seen:
            seen.add(fp)
            unique.append(doc)
    return unique
