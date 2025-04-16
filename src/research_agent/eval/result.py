from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvalResult:
    query: str
    expected: str
    generated: str
    scores: dict[str, float] = field(default_factory=dict)
    passed: bool = False

    @property
    def mean_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(self.scores.values()) / len(self.scores)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "expected": self.expected,
            "generated": self.generated,
            "scores": self.scores,
            "mean_score": self.mean_score,
            "passed": self.passed,
        }


def threshold_check(result: EvalResult, threshold: float = 0.6) -> EvalResult:
    result.passed = all(v >= threshold for v in result.scores.values())
    return result
