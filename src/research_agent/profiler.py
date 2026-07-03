from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class NodeMetrics:
    call_count: int = 0
    total_ms: float = 0.0
    error_count: int = 0
    last_call_ms: float = 0.0


class GraphProfiler:
    """Track per-node latency and error rates during graph execution."""

    def __init__(self) -> None:
        self._metrics: dict[str, NodeMetrics] = defaultdict(NodeMetrics)

    def record_call(self, node: str, duration_ms: float, error: bool = False) -> None:
        m = self._metrics[node]
        m.call_count += 1
        m.total_ms += duration_ms
        m.last_call_ms = duration_ms
        if error:
            m.error_count += 1
        logger.debug("node=%s duration=%.1fms error=%s", node, duration_ms, error)

    def report(self) -> dict[str, dict]:
        return {
            node: {
                "calls": m.call_count,
                "avg_ms": round(m.total_ms / m.call_count, 2) if m.call_count else 0,
                "total_ms": round(m.total_ms, 2),
                "errors": m.error_count,
            }
            for node, m in self._metrics.items()
        }

    def slowest_node(self) -> str | None:
        if not self._metrics:
            return None
        return max(self._metrics, key=lambda n: self._metrics[n].total_ms)
