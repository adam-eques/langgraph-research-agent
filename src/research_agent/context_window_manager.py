from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ContextWindowManager:
    """Manage multi-turn context within LLM token limits using rolling windows."""

    def __init__(self, max_tokens: int = 8000, chars_per_token: int = 4) -> None:
        self.max_tokens = max_tokens
        self.chars_per_token = chars_per_token
        self._messages: list[dict[str, str]] = []

    def _estimate(self, msg: dict) -> int:
        return max(1, len(str(msg.get("content", ""))) // self.chars_per_token)

    def add(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})
        self._trim()

    def _trim(self) -> None:
        total = sum(self._estimate(m) for m in self._messages)
        while total > self.max_tokens and len(self._messages) > 1:
            removed = self._messages.pop(0)
            total -= self._estimate(removed)
            logger.debug("Trimmed message from context (role=%s)", removed.get("role"))

    def get_messages(self) -> list[dict[str, str]]:
        return list(self._messages)

    def clear(self) -> None:
        self._messages.clear()

    @property
    def message_count(self) -> int:
        return len(self._messages)
