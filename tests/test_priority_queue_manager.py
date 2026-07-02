from __future__ import annotations
from research_agent.priority_queue_manager import PriorityQueueManager, PriorityItem


def test_enqueue_and_dequeue_order():
    pq = PriorityQueueManager()
    pq.enqueue("low", priority=10)
    pq.enqueue("high", priority=1)
    pq.enqueue("medium", priority=5)
    first = pq.dequeue()
    assert first.payload == "high"


def test_dequeue_empty():
    pq = PriorityQueueManager()
    assert pq.dequeue() is None


def test_peek_does_not_remove():
    pq = PriorityQueueManager()
    pq.enqueue("item", priority=3)
    pq.peek()
    assert pq.size == 1


def test_drain():
    pq = PriorityQueueManager()
    pq.enqueue("a", priority=2)
    pq.enqueue("b", priority=1)
    items = pq.drain()
    assert len(items) == 2 and pq.size == 0


def test_filter_by_tag():
    pq = PriorityQueueManager()
    pq.enqueue("task1", tags=["urgent"])
    pq.enqueue("task2", tags=["low"])
    pq.enqueue("task3", tags=["urgent"])
    urgent = pq.filter_by_tag("urgent")
    assert len(urgent) == 2


def test_stats():
    pq = PriorityQueueManager()
    pq.enqueue("x")
    pq.enqueue("y")
    pq.dequeue()
    s = pq.stats
    assert s["total_enqueued"] == 2 and s["total_dequeued"] == 1 and s["size"] == 1
