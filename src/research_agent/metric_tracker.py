from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MetricSample:
    value: float
    timestamp: float = field(default_factory=time.time)
    labels: dict = field(default_factory=dict)


class MetricTracker:
    def __init__(self) -> None:
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._samples: dict[str, list[MetricSample]] = defaultdict(list)

    def increment(self, name: str, amount: float = 1.0) -> None:
        self._counters[name] += amount

    def gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def record(self, name: str, value: float, labels: dict | None = None) -> None:
        self._samples[name].append(MetricSample(value=value, labels=labels or {}))

    def counter(self, name: str) -> float:
        return self._counters.get(name, 0.0)

    def get_gauge(self, name: str) -> float | None:
        return self._gauges.get(name)

    def avg(self, name: str) -> float | None:
        samples = self._samples.get(name)
        if not samples:
            return None
        return sum(s.value for s in samples) / len(samples)

    def p95(self, name: str) -> float | None:
        samples = self._samples.get(name)
        if not samples:
            return None
        values = sorted(s.value for s in samples)
        idx = max(0, int(len(values) * 0.95) - 1)
        return values[idx]

    def reset(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._samples.clear()
