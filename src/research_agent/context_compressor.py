from __future__ import annotations

import logging
import re
from typing import ClassVar

logger = logging.getLogger(__name__)


class ContextCompressor:
    """Compress research context by removing boilerplate and redundant sentences."""

    _BOILERPLATE: ClassVar[list[str]] = [
        r"cookie policy",
        r"privacy policy",
        r"terms of service",
        r"all rights reserved",
        r"subscribe to",
        r"click here",
        r"sign up for",
        r"advertisement",
    ]

    def __init__(self, max_chars: int = 8000) -> None:
        self.max_chars = max_chars

    def strip_boilerplate(self, text: str) -> str:
        for pattern in self._BOILERPLATE:
            text = re.sub(rf"[^\n]*{pattern}[^\n]*\n?", "", text, flags=re.IGNORECASE)
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
            marker = " [compressed]"
            keep = max(0, self.max_chars - len(marker))
            text = text[:keep] + marker
            logger.debug("Context compressed to %d chars", self.max_chars)
        return text
