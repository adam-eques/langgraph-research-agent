from __future__ import annotations

from research_agent.feedback import FeedbackStore


def test_record_and_retrieve(tmp_path):
    store = FeedbackStore(path=str(tmp_path / "fb.jsonl"))
    store.record("What is AI?", 5, "Great answer")
    fb = store.all_feedback()
    assert len(fb) == 1
    assert fb[0]["rating"] == 5


def test_average_rating(tmp_path):
    store = FeedbackStore(path=str(tmp_path / "fb.jsonl"))
    store.record("q1", 4)
    store.record("q2", 2)
    assert abs(store.average_rating() - 3.0) < 0.001


def test_low_rated_filter(tmp_path):
    store = FeedbackStore(path=str(tmp_path / "fb.jsonl"))
    store.record("q1", 5)
    store.record("q2", 2)
    assert len(store.low_rated(threshold=3)) == 1


def test_empty_store_average(tmp_path):
    store = FeedbackStore(path=str(tmp_path / "nofile.jsonl"))
    assert store.average_rating() == 0.0
