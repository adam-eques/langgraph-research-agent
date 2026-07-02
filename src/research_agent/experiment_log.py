from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ExperimentLog:
    """Log LLM experiment runs with parameters and results for comparison."""

    def __init__(self, path: str = "experiments.jsonl") -> None:
        self._path = Path(path)

    def log(
        self,
        experiment_id: str,
        model: str,
        params: dict[str, Any],
        result: dict[str, Any],
    ) -> None:
        entry = {
            "experiment_id": experiment_id,
            "model": model,
            "params": params,
            "result": result,
        }
        with self._path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
        logger.debug("Logged experiment %s (%s)", experiment_id, model)

    def load_all(self) -> list[dict]:
        if not self._path.exists():
            return []
        return [json.loads(line) for line in self._path.read_text().splitlines() if line.strip()]

    def filter_by_model(self, model: str) -> list[dict]:
        return [e for e in self.load_all() if e.get("model") == model]
