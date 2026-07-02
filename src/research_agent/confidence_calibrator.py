from __future__ import annotations

import math


def platt_scaling(raw_score: float, a: float = 1.0, b: float = 0.0) -> float:
    logit = a * raw_score + b
    return 1.0 / (1.0 + math.exp(-logit))


def isotonic_calibration(scores: list[float], labels: list[int]) -> list[float]:
    if not scores or not labels or len(scores) != len(labels):
        return scores
    pairs = sorted(zip(scores, labels))
    calibrated = [p[1] for p in pairs]
    result: list[float] = []
    for i, s in enumerate(scores):
        idx = min(range(len(pairs)), key=lambda j: abs(pairs[j][0] - s))
        result.append(float(calibrated[idx]))
    return result


def calibrate_confidence(
    raw_score: float,
    source_count: int = 1,
    fact_check_passed: bool = True,
    evidence_strength: float = 0.5,
) -> float:
    base = platt_scaling(raw_score)
    source_boost = min(0.1 * (source_count - 1), 0.2)
    fact_boost = 0.1 if fact_check_passed else -0.15
    evidence_adj = (evidence_strength - 0.5) * 0.2
    calibrated = base + source_boost + fact_boost + evidence_adj
    return round(max(0.0, min(1.0, calibrated)), 4)


def confidence_label(score: float) -> str:
    if score >= 0.85:
        return "very_high"
    if score >= 0.7:
        return "high"
    if score >= 0.5:
        return "medium"
    if score >= 0.3:
        return "low"
    return "very_low"
