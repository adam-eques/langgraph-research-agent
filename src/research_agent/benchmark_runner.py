from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class BenchmarkResult:
    name: str
    elapsed_ms: float
    iterations: int
    mean_ms: float
    min_ms: float
    max_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "elapsed_ms": round(self.elapsed_ms, 4),
            "iterations": self.iterations,
            "mean_ms": round(self.mean_ms, 4),
            "min_ms": round(self.min_ms, 4),
            "max_ms": round(self.max_ms, 4),
        }


class BenchmarkRunner:
    def __init__(self) -> None:
        self._results: list[BenchmarkResult] = []

    def run(
        self,
        name: str,
        fn: Callable[[], Any],
        iterations: int = 10,
        warmup: int = 1,
    ) -> BenchmarkResult:
        for _ in range(warmup):
            fn()

        samples: list[float] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            fn()
            samples.append((time.perf_counter() - t0) * 1000)

        result = BenchmarkResult(
            name=name,
            elapsed_ms=sum(samples),
            iterations=iterations,
            mean_ms=sum(samples) / iterations,
            min_ms=min(samples),
            max_ms=max(samples),
        )
        self._results.append(result)
        return result

    def compare(self, baseline_name: str) -> dict[str, float]:
        baseline = next((r for r in self._results if r.name == baseline_name), None)
        if baseline is None:
            return {}
        ratios: dict[str, float] = {}
        for r in self._results:
            if r.name != baseline_name:
                ratios[r.name] = r.mean_ms / baseline.mean_ms if baseline.mean_ms else 0.0
        return ratios

    def summary(self) -> list[dict]:
        return [r.to_dict() for r in self._results]

    def fastest(self) -> BenchmarkResult | None:
        if not self._results:
            return None
        return min(self._results, key=lambda r: r.mean_ms)
