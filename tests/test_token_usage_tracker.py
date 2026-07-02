from __future__ import annotations
from research_agent.token_usage_tracker import TokenUsageTracker, TokenUsageRecord


def test_record_basic():
    tracker = TokenUsageTracker()
    rec = tracker.record("s1", "gpt-4", 100, 50)
    assert rec.total_tokens == 150


def test_total_tokens():
    tracker = TokenUsageTracker()
    tracker.record("s1", "gpt-4", 100, 50)
    tracker.record("s2", "claude", 200, 80)
    assert tracker.total_tokens() == 430


def test_by_model():
    tracker = TokenUsageTracker()
    tracker.record("s1", "gpt-4", 100, 50)
    tracker.record("s2", "gpt-4", 200, 60)
    tracker.record("s3", "claude", 50, 20)
    by_model = tracker.by_model()
    assert by_model["gpt-4"] == 410 and by_model["claude"] == 70


def test_by_session():
    tracker = TokenUsageTracker()
    tracker.record("sessionA", "gpt-4", 100, 50)
    tracker.record("sessionA", "gpt-4", 80, 40)
    tracker.record("sessionB", "claude", 200, 80)
    recs = tracker.by_session("sessionA")
    assert len(recs) == 2


def test_session_total():
    tracker = TokenUsageTracker()
    tracker.record("s1", "m", 100, 50)
    tracker.record("s1", "m", 60, 30)
    assert tracker.session_total("s1") == 240


def test_summary():
    tracker = TokenUsageTracker()
    tracker.record("s", "model", 100, 50)
    s = tracker.summary()
    assert s["total_records"] == 1 and s["total_tokens"] == 150
