from __future__ import annotations

from collections import deque
from typing import Any


class AgentMemory:
    def __init__(self, max_turns: int = 20) -> None:
        self._max = max_turns
        self._turns: deque[dict[str, Any]] = deque(maxlen=max_turns)
        self._facts: dict[str, Any] = {}

    def add_turn(self, role: str, content: str, metadata: dict | None = None) -> None:
        self._turns.append({"role": role, "content": content, "meta": metadata or {}})

    def remember_fact(self, key: str, value: Any) -> None:
        self._facts[key] = value

    def recall_fact(self, key: str, default: Any = None) -> Any:
        return self._facts.get(key, default)

    def forget_fact(self, key: str) -> bool:
        return self._facts.pop(key, None) is not None

    def get_turns(self, n: int | None = None) -> list[dict[str, Any]]:
        turns = list(self._turns)
        return turns[-n:] if n else turns

    def to_messages(self, n: int | None = None) -> list[dict[str, str]]:
        return [{"role": t["role"], "content": t["content"]} for t in self.get_turns(n)]

    def clear(self) -> None:
        self._turns.clear()
        self._facts.clear()

    @property
    def turn_count(self) -> int:
        return len(self._turns)
