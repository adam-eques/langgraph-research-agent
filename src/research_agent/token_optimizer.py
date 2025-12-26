from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class TokenOptimizer:
    """Optimize message sequences to minimize token usage while preserving context."""

    def __init__(
        self,
        target_tokens: int = 6000,
        chars_per_token: int = 4,
    ) -> None:
        self.target_tokens = target_tokens
        self.chars_per_token = chars_per_token

    def _estimate(self, text: str) -> int:
        return max(1, len(text) // self.chars_per_token)

    def optimize_messages(self, messages: list[dict]) -> list[dict]:
        total = sum(self._estimate(str(m.get("content", ""))) for m in messages)
        if total <= self.target_tokens:
            return messages
        logger.debug("Optimizing %d messages (est. %d tokens)", len(messages), total)
        # Keep system messages; trim oldest non-system messages first
        system = [m for m in messages if m.get("role") == "system"]
        other = [m for m in messages if m.get("role") != "system"]
        result = list(system)
        budget = self.target_tokens - sum(self._estimate(str(m.get("content", ""))) for m in system)
        for msg in reversed(other):
            tokens = self._estimate(str(msg.get("content", "")))
            if budget - tokens >= 0:
                result.insert(len(system), msg)
                budget -= tokens
            else:
                break
        return result
