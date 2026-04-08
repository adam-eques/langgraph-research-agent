from __future__ import annotations
import pytest
from research_agent.feedback_processor import Feedback, FeedbackProcessor


def test_submit_and_average(tmp_path):
    fp = FeedbackProcessor(str(tmp_path / "fb.jsonl"))
    fp.submit(Feedback("s1", "Q?", 4))
    fp.submit(Feedback("s1", "Q2?", 2))
    assert fp.average_rating() == 3.0


def test_by_session(tmp_path):
    fp = FeedbackProcessor(str(tmp_path / "fb.jsonl"))
    fp.submit(Feedback("s1", "Q?", 5))
    fp.submit(Feedback("s2", "Q2?", 3))
    assert len(fp.by_session("s1")) == 1


def test_low_rated(tmp_path):
    fp = FeedbackProcessor(str(tmp_path / "fb.jsonl"))
    fp.submit(Feedback("s1", "Q?", 1, helpful=False))
    fp.submit(Feedback("s1", "Q2?", 5))
    assert len(fp.low_rated(threshold=2)) == 1


def test_invalid_rating():
    with pytest.raises(ValueError):
        Feedback("s1", "Q", rating=0)
