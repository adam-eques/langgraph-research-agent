from __future__ import annotations

import logging
from typing import Any, cast

logger = logging.getLogger(__name__)

_HEADER = "## Context\n\n"
_DOC_SEP = "\n---\n"


def format_document(doc: dict, index: int = 0) -> str:
    content = doc.get("content", "").strip()
    source = doc.get("source", "")
    header = f"[{index + 1}] {source}\n" if source else f"[{index + 1}]\n"
    return cast(str, header + content)


def build_context(
    documents: list[dict],
    max_chars: int = 8000,
    include_header: bool = True,
) -> str:
    parts: list[str] = []
    total_chars = 0
    for i, doc in enumerate(documents):
        formatted = format_document(doc, i)
        if total_chars + len(formatted) > max_chars:
            logger.debug("Context truncated after %d documents", i)
            break
        parts.append(formatted)
        total_chars += len(formatted)

    body = _DOC_SEP.join(parts)
    return (_HEADER + body) if include_header else body


def build_messages(
    system_prompt: str,
    user_query: str,
    context: str = "",
    history: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = list(history or [])
    user_content = f"{context}\n\n{user_query}".strip() if context else user_query
    messages.append({"role": "user", "content": user_content})
    return messages


def summarize_notes(notes: list[str], max_chars: int = 5000) -> str:
    """Join research notes into a single block, truncated to *max_chars*."""
    joined = "\n\n".join(n.strip() for n in notes if n.strip())
    if len(joined) > max_chars:
        return joined[:max_chars].rstrip() + " …"
    return joined


def format_citations(citations: list[dict]) -> str:
    """Render citation dicts as a numbered ``Sources`` block (empty if none)."""
    if not citations:
        return ""
    lines = ["Sources:"]
    for i, cite in enumerate(citations, 1):
        source = cite.get("source", "unknown")
        excerpt = cite.get("excerpt", "")
        line = f"[{i}] {source}"
        if excerpt:
            line += f" — {excerpt[:150].strip()}"
        lines.append(line)
    return "\n".join(lines)
