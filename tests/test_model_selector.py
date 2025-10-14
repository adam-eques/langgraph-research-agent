from __future__ import annotations
from research_agent.model_selector import select_model, list_models


def test_list_models_not_empty():
    assert len(list_models()) > 0


def test_select_cheap_anthropic():
    model = select_model(prefer_cheap=True, provider="anthropic")
    assert "claude" in model.model_id
    assert model.cost_per_1k_tokens < 0.003


def test_select_vision_model():
    model = select_model(needs_vision=True, provider="anthropic")
    assert model.supports_vision is True


def test_select_requires_context():
    model = select_model(required_context=128000, provider="anthropic")
    assert model.context_window >= 128000
