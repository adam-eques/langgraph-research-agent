from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class OutputBuffer:
    """Buffer streaming tokens and yield them in configurable chunk sizes."""

    def __init__(self, chunk_size: int = 10) -> None:
        self._buffer: list[str] = []
        self._chunk_size = chunk_size

    def push(self, token: str) -> str | None:
        self._buffer.append(token)
        if len(self._buffer) >= self._chunk_size:
            return self.flush()
        return None

    def flush(self) -> str:
        text = "".join(self._buffer)
        self._buffer.clear()
        return text

    def __len__(self) -> int:
        return len(self._buffer)
