from __future__ import annotations

import logging
import re
from typing import ClassVar

logger = logging.getLogger(__name__)


class ContextCompressor:
    """Compress research context by removing boilerplate and redundant sentences."""

    _BOILERPLATE: ClassVar[list[str]] = [
        r"(?i)cookie policy",
        r"(?i)privacy policy",
        r"(?i)terms of service",
        r"(?i)all rights reserved",
        r"(?i)subscribe to",
        r"(?i)click here",
        r"(?i)sign up for",
        r"(?i)advertisement",
    ]

    def __init__(self, max_chars: int = 8000) -> None:
        self.max_chars = max_chars

    def strip_boilerplate(self, text: str) -> str:
        for pattern in self._BOILERPLATE:
            text = re.sub(rf"[^\n]*{pattern}[^\n]*\n?", "", text)
        return text.strip()

    def remove_duplicate_sentences(self, text: str) -> str:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        seen, unique = set(), []
        for s in sentences:
            key = s.strip().lower()[:60]
            if key and key not in seen:
                seen.add(key)
                unique.append(s)
        return " ".join(unique)

    def compress(self, text: str) -> str:
        text = self.strip_boilerplate(text)
        text = self.remove_duplicate_sentences(text)
        if len(text) > self.max_chars:
            text = text[: self.max_chars] + " [compressed]"
            logger.debug("Context compressed to %d chars", self.max_chars)
        return text
