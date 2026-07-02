from __future__ import annotations

from research_agent.progress_tracker import ProgressTracker


def test_update_increments():
    pt = ProgressTracker(total=10, label="docs")
    pt.update(3)
    assert pt.done == 3


def test_remaining():
    pt = ProgressTracker(total=10)
    pt.update(4)
    assert pt.remaining == 6


def test_pct():
    pt = ProgressTracker(total=100)
    pt.update(50)
    assert pt.pct == 50.0


def test_elapsed_is_positive():
    pt = ProgressTracker(total=5)
    pt.update(1)
    assert pt.elapsed_s >= 0
