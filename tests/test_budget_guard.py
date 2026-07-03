from __future__ import annotations

from research_agent.budget_guard import TokenBudgetGuard


def test_consume_within_budget():
    guard = TokenBudgetGuard(max_tokens=100)
    assert guard.consume(50) is True
    assert guard.remaining == 50


def test_consume_exceeds_budget():
    guard = TokenBudgetGuard(max_tokens=100)
    guard.consume(80)
    assert guard.consume(30) is False


def test_used_tracks_total():
    guard = TokenBudgetGuard(max_tokens=1000)
    guard.consume(200)
    guard.consume(300)
    assert guard.used == 500


def test_reset():
    guard = TokenBudgetGuard(max_tokens=100)
    guard.consume(90)
    guard.reset()
    assert guard.used == 0
    assert guard.remaining == 100
