from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

_HEADER = "## Context\n\n"
_DOC_SEP = "\n---\n"


def format_document(doc: dict, index: int = 0) -> str:
    content = doc.get("content", "").strip()
    source = doc.get("source", "")
    header = f"[{index + 1}] {source}\n" if source else f"[{index + 1}]\n"
    return header + content


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
