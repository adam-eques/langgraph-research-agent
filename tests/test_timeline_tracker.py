from __future__ import annotations
from research_agent.timeline_tracker import TimelineTracker, extract_date, TimelineEvent


def test_extract_date_iso():
    assert extract_date("Published on 2024-03-15.") == "2024-03-15"


def test_extract_date_year_only():
    result = extract_date("This happened in 2023.")
    assert "2023" in result


def test_extract_date_none():
    assert extract_date("No dates here.") is None


def test_add_event():
    tracker = TimelineTracker()
    e = tracker.add_event("2024-01-01", "Project launched", tags=["launch"])
    assert tracker.event_count == 1 and "launch" in e.tags


def test_extract_and_add():
    tracker = TimelineTracker()
    e = tracker.extract_and_add("In 2023 the framework was released.")
    assert e is not None and "2023" in e.timestamp


def test_sorted_events():
    tracker = TimelineTracker()
    tracker.add_event("2024-06-01", "Later")
    tracker.add_event("2023-01-01", "Earlier")
    events = tracker.sorted_events()
    assert events[0].timestamp < events[1].timestamp


def test_filter_by_year():
    tracker = TimelineTracker()
    tracker.add_event("2023-05-01", "A")
    tracker.add_event("2024-09-01", "B")
    result = tracker.filter_by_year(2023)
    assert len(result) == 1 and "2023" in result[0].timestamp


def test_to_markdown():
    tracker = TimelineTracker()
    tracker.add_event("2024-01-01", "Event one")
    md = tracker.to_markdown()
    assert "Timeline" in md and "2024-01-01" in md
