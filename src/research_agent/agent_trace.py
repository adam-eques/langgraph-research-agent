from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AgentTrace:
    """Record and replay agent execution traces for debugging."""

    def __init__(self) -> None:
        self._steps: list[dict[str, Any]] = []

    def record(self, node: str, inputs: dict, outputs: dict, duration_ms: float) -> None:
        self._steps.append(
            {
                "node": node,
                "inputs_keys": list(inputs.keys()),
                "outputs_keys": list(outputs.keys()),
                "duration_ms": round(duration_ms, 2),
            }
        )

    @property
    def steps(self) -> list[dict]:
        return list(self._steps)

    def summary(self) -> dict:
        if not self._steps:
            return {"total_steps": 0, "total_ms": 0.0, "nodes": []}
        return {
            "total_steps": len(self._steps),
            "total_ms": round(sum(s["duration_ms"] for s in self._steps), 2),
            "nodes": [s["node"] for s in self._steps],
        }

    def to_json(self) -> str:
        return json.dumps({"steps": self._steps, "summary": self.summary()}, indent=2)

    def save(self, path: str) -> None:
        Path(path).write_text(self.to_json())
        logger.debug("Trace saved to %s (%d steps)", path, len(self._steps))
