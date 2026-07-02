from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


class AdaptiveChunker:
    """Adjust chunk size based on document type and estimated complexity."""

    _CODE_PATTERN = re.compile(r"```|def |class |import |from .+ import")
    _TABLE_PATTERN = re.compile(r"\|.+\|.+\|")

    def __init__(
        self,
        base_size: int = 1000,
        code_size: int = 500,
        table_size: int = 400,
        overlap: int = 100,
    ) -> None:
        self.base_size = base_size
        self.code_size = code_size
        self.table_size = table_size
        self.overlap = overlap

    def detect_content_type(self, text: str) -> str:
        if self._CODE_PATTERN.search(text):
            return "code"
        if self._TABLE_PATTERN.search(text):
            return "table"
        return "prose"

    def chunk(self, text: str) -> list[str]:
        content_type = self.detect_content_type(text)
        size = {"code": self.code_size, "table": self.table_size}.get(content_type, self.base_size)
        logger.debug("Chunking %d chars as %s (size=%d)", len(text), content_type, size)
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + size, len(text))
            chunks.append(text[start:end])
            start = end - self.overlap if end < len(text) else end
        return chunks
