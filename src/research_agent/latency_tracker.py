from __future__ import annotations

import time
from collections import defaultdict
from contextlib import contextmanager


class LatencyTracker:
    def __init__(self) -> None:
        self._samples: dict[str, list[float]] = defaultdict(list)

    @contextmanager
    def track(self, name: str):
        start = time.monotonic()
        try:
            yield
        finally:
            elapsed_ms = (time.monotonic() - start) * 1000
            self._samples[name].append(elapsed_ms)

    def record(self, name: str, latency_ms: float) -> None:
        self._samples[name].append(latency_ms)

    def mean(self, name: str) -> float | None:
        s = self._samples.get(name)
        return sum(s) / len(s) if s else None

    def p50(self, name: str) -> float | None:
        return self._percentile(name, 50)

    def p99(self, name: str) -> float | None:
        return self._percentile(name, 99)

    def _percentile(self, name: str, pct: int) -> float | None:
        s = self._samples.get(name)
        if not s:
            return None
        sorted_s = sorted(s)
        idx = max(0, int(len(sorted_s) * pct / 100) - 1)
        return sorted_s[idx]

    def summary(self, name: str) -> dict:
        return {
            "name": name,
            "count": len(self._samples.get(name, [])),
            "mean_ms": self.mean(name),
            "p50_ms": self.p50(name),
            "p99_ms": self.p99(name),
        }

    def all_summaries(self) -> list[dict]:
        return [self.summary(n) for n in sorted(self._samples)]
