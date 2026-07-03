from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ModelSpec:
    model_id: str
    context_window: int
    cost_per_1k_tokens: float
    supports_vision: bool = False
    supports_function_calling: bool = True


_MODELS: dict[str, ModelSpec] = {
    "claude-3-5-sonnet-20241022": ModelSpec(
        model_id="claude-3-5-sonnet-20241022",
        context_window=200000,
        cost_per_1k_tokens=0.003,
        supports_vision=True,
    ),
    "claude-3-haiku-20240307": ModelSpec(
        model_id="claude-3-haiku-20240307",
        context_window=200000,
        cost_per_1k_tokens=0.00025,
    ),
    "gpt-4o": ModelSpec(
        model_id="gpt-4o",
        context_window=128000,
        cost_per_1k_tokens=0.005,
        supports_vision=True,
    ),
    "gpt-4o-mini": ModelSpec(
        model_id="gpt-4o-mini",
        context_window=128000,
        cost_per_1k_tokens=0.00015,
    ),
}


def select_model(
    required_context: int = 0,
    prefer_cheap: bool = False,
    needs_vision: bool = False,
    provider: str = "anthropic",
) -> ModelSpec:
    candidates = [m for m in _MODELS.values() if m.context_window >= required_context]
    if needs_vision:
        candidates = [m for m in candidates if m.supports_vision]
    if provider == "anthropic":
        candidates = [m for m in candidates if "claude" in m.model_id]
    elif provider == "openai":
        candidates = [m for m in candidates if "gpt" in m.model_id]
    if not candidates:
        return next(iter(_MODELS.values()))
    if prefer_cheap:
        return min(candidates, key=lambda m: m.cost_per_1k_tokens)
    return max(candidates, key=lambda m: m.context_window)


def list_models() -> list[str]:
    return list(_MODELS.keys())
