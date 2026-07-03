from __future__ import annotations

from research_agent.confidence_calibrator import (
    calibrate_confidence,
    confidence_label,
    platt_scaling,
)


def test_platt_scaling_range():
    assert 0.0 < platt_scaling(0.0) < 1.0
    assert 0.0 < platt_scaling(1.0) < 1.0


def test_calibrate_high_confidence():
    score = calibrate_confidence(0.8, source_count=3, fact_check_passed=True, evidence_strength=0.9)
    assert score > 0.5


def test_calibrate_low_without_factcheck():
    score = calibrate_confidence(0.3, fact_check_passed=False)
    assert score < 0.5


def test_confidence_labels():
    assert confidence_label(0.9) == "very_high"
    assert confidence_label(0.6) == "medium"
    assert confidence_label(0.1) == "very_low"
