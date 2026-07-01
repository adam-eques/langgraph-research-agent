from __future__ import annotations

import json
import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class PerfLogger:
    def __init__(self, log_path: str = "perf.jsonl") -> None:
        self._path = Path(log_path)
        self._session: list[dict] = []

    def log(
        self,
        operation: str,
        duration_ms: float,
        tokens_in: int = 0,
        tokens_out: int = 0,
        model: str = "",
        extra: dict | None = None,
    ) -> None:
        record = {
            "ts": time.time(),
            "operation": operation,
            "duration_ms": round(duration_ms, 3),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "total_tokens": tokens_in + tokens_out,
            "model": model,
            **(extra or {}),
        }
        self._session.append(record)
        with self._path.open("a") as f:
            f.write(json.dumps(record) + "\n")
        logger.debug("PerfLog: %s %.1fms", operation, duration_ms)

    def session_stats(self) -> dict:
        if not self._session:
            return {}
        durations = [r["duration_ms"] for r in self._session]
        total_tokens = sum(r["total_tokens"] for r in self._session)
        return {
            "count": len(self._session),
            "total_duration_ms": round(sum(durations), 2),
            "mean_duration_ms": round(sum(durations) / len(durations), 2),
            "max_duration_ms": round(max(durations), 2),
            "total_tokens": total_tokens,
        }
