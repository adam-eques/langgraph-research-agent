from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator, Any

logger = logging.getLogger(__name__)


class TokenBudgetGuard:
    """Abort generation early when token budget is exhausted."""

    def __init__(self, max_tokens: int) -> None:
        self.max_tokens = max_tokens
        self._used = 0

    def consume(self, tokens: int) -> bool:
        self._used += tokens
        if self._used > self.max_tokens:
            logger.warning(
                "Token budget exceeded: used=%d max=%d", self._used, self.max_tokens
            )
            return False
        return True

    @property
    def remaining(self) -> int:
        return max(0, self.max_tokens - self._used)

    @property
    def used(self) -> int:
        return self._used

    def reset(self) -> None:
        self._used = 0
