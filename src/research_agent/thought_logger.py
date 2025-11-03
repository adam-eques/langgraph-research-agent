from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ThoughtLogger:
    """Capture agent chain-of-thought reasoning steps for debugging."""

    def __init__(self, path: str | None = None) -> None:
        self._thoughts: list[dict[str, Any]] = []
        self._path = Path(path) if path else None

    def log(self, agent: str, thought: str, step: int | None = None) -> None:
        entry = {"agent": agent, "thought": thought, "step": step}
        self._thoughts.append(entry)
        logger.debug("[%s] thought: %s", agent, thought[:120])
        if self._path:
            with self._path.open("a") as f:
                f.write(json.dumps(entry) + "\n")

    def for_agent(self, agent: str) -> list[dict]:
        return [t for t in self._thoughts if t["agent"] == agent]

    def all_thoughts(self) -> list[dict]:
        return list(self._thoughts)

    def clear(self) -> None:
        self._thoughts.clear()
