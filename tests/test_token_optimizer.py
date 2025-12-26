from __future__ import annotations

from research_agent.token_optimizer import TokenOptimizer


def test_short_messages_unchanged():
    opt = TokenOptimizer(target_tokens=10000)
    msgs = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]
    result = opt.optimize_messages(msgs)
    assert result == msgs


def test_trims_to_budget():
    opt = TokenOptimizer(target_tokens=10, chars_per_token=1)
    msgs = [{"role": "user", "content": "a" * 5}, {"role": "user", "content": "b" * 5}]
    result = opt.optimize_messages(msgs)
    total = sum(len(m["content"]) for m in result)
    assert total <= 10


def test_preserves_system_messages():
    opt = TokenOptimizer(target_tokens=5, chars_per_token=1)
    msgs = [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "u" * 100},
    ]
    result = opt.optimize_messages(msgs)
    assert any(m["role"] == "system" for m in result)
