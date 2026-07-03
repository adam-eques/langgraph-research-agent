from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ContextTruncator:
    """Truncate large document context to fit LLM token budgets."""

    def __init__(self, max_chars: int = 16000, overlap: int = 200) -> None:
        self.max_chars = max_chars
        self.overlap = overlap

    def truncate(self, text: str) -> str:
        if len(text) <= self.max_chars:
            return text
        truncated = text[: self.max_chars]
        logger.debug(
            "Context truncated from %d to %d chars (overlap=%d)",
            len(text),
            self.max_chars,
            self.overlap,
        )
        if self.overlap > 0 and len(text) >= self.max_chars + self.overlap:
            truncated += "\n\n[...truncated...]\n\n" + text[-self.overlap :]
        return truncated

    def truncate_list(self, chunks: list[str]) -> list[str]:
        total = 0
        result = []
        for chunk in chunks:
            if total + len(chunk) > self.max_chars:
                break
            result.append(chunk)
            total += len(chunk)
        return result
