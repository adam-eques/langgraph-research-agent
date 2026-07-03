from __future__ import annotations

import pytest

from research_agent.token_budget import TokenBudget


def test_consume_within_budget():
    tb = TokenBudget(1000)
    assert tb.consume(500) is True and tb.used == 500


def test_consume_over_budget():
    tb = TokenBudget(100)
    assert tb.consume(150) is False and tb.used == 0


def test_is_exhausted():
    tb = TokenBudget(10)
    tb.consume(10)
    assert tb.is_exhausted()


def test_reset():
    tb = TokenBudget(100)
    tb.consume(80)
    tb.reset()
    assert tb.used == 0 and tb.remaining == 100


def test_pct_used():
    tb = TokenBudget(200)
    tb.consume(100)
    assert tb.pct_used() == 50.0


def test_invalid_total():
    with pytest.raises(ValueError):
        TokenBudget(0)
