from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NodeRun:
    node_name: str
    started_at: float
    ended_at: float | None = None
    status: str = "pending"
    output_keys: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def duration_ms(self) -> float | None:
        if self.ended_at is None:
            return None
        return (self.ended_at - self.started_at) * 1000


class PipelineMonitor:
    def __init__(self, pipeline_id: str) -> None:
        self.pipeline_id = pipeline_id
        self._runs: list[NodeRun] = []
        self._global_start: float = time.monotonic()

    def node_started(self, node_name: str) -> NodeRun:
        run = NodeRun(node_name=node_name, started_at=time.monotonic())
        self._runs.append(run)
        return run

    def node_finished(self, run: NodeRun, output: dict[str, Any] | None = None) -> None:
        run.ended_at = time.monotonic()
        run.status = "success"
        run.output_keys = list(output.keys()) if output else []

    def node_failed(self, run: NodeRun, error: str) -> None:
        run.ended_at = time.monotonic()
        run.status = "error"
        run.error = error

    @property
    def total_duration_ms(self) -> float:
        return (time.monotonic() - self._global_start) * 1000

    def summary(self) -> dict:
        return {
            "pipeline_id": self.pipeline_id,
            "total_duration_ms": round(self.total_duration_ms, 2),
            "nodes_run": len(self._runs),
            "nodes_succeeded": sum(1 for r in self._runs if r.status == "success"),
            "nodes_failed": sum(1 for r in self._runs if r.status == "error"),
            "runs": [
                {
                    "node": r.node_name,
                    "status": r.status,
                    "duration_ms": round(r.duration_ms, 2) if r.duration_ms else None,
                }
                for r in self._runs
            ],
        }
