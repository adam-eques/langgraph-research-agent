from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class TokenBudget:
    def __init__(self, total: int) -> None:
        if total <= 0:
            raise ValueError("total must be positive")
        self._total = total
        self._used = 0

    @property
    def total(self) -> int:
        return self._total

    @property
    def used(self) -> int:
        return self._used

    @property
    def remaining(self) -> int:
        return max(0, self._total - self._used)

    def consume(self, tokens: int) -> bool:
        if tokens < 0:
            raise ValueError("tokens cannot be negative")
        if self._used + tokens > self._total:
            logger.warning(
                "Token budget exceeded: used=%d requested=%d total=%d",
                self._used,
                tokens,
                self._total,
            )
            return False
        self._used += tokens
        return True

    def reset(self) -> None:
        self._used = 0

    def pct_used(self) -> float:
        return self._used / self._total * 100.0

    def is_exhausted(self) -> bool:
        return self._used >= self._total
