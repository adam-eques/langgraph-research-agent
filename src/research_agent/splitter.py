from __future__ import annotations

import re
from typing import Protocol


class Tokenizer(Protocol):
    def encode(self, text: str) -> list[int]: ...
    def decode(self, tokens: list[int]) -> str: ...


def sentence_split(text: str) -> list[str]:
    """Split text into sentences using simple heuristics."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def paragraph_split(text: str) -> list[str]:
    """Split text into paragraphs on double-newlines."""
    return [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]


def token_aware_split(text: str, max_tokens: int, chars_per_token: int = 4) -> list[str]:
    """Split text into segments fitting within token budget."""
    max_chars = max_tokens * chars_per_token
    if len(text) <= max_chars:
        return [text]
    sentences = sentence_split(text)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for s in sentences:
        if current_len + len(s) > max_chars and current:
            chunks.append(" ".join(current))
            current, current_len = [s], len(s)
        else:
            current.append(s)
            current_len += len(s)
    if current:
        chunks.append(" ".join(current))
    return chunks
