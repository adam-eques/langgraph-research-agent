from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

REQUIRED_KEYS = ["anthropic_api_key"]
OPTIONAL_KEYS = {"model": "claude-3-5-sonnet-20241022", "temperature": 0.0, "max_tokens": 4096}


def validate_config(config: dict) -> list[str]:
    errors = []
    for key in REQUIRED_KEYS:
        if not config.get(key):
            errors.append(f"Missing required config: {key}")
    temp = config.get("temperature", 0.0)
    if not isinstance(temp, (int, float)) or not (0.0 <= temp <= 2.0):
        errors.append(f"temperature must be between 0.0 and 2.0, got: {temp}")
    max_tok = config.get("max_tokens", 4096)
    if not isinstance(max_tok, int) or max_tok < 1:
        errors.append(f"max_tokens must be a positive integer, got: {max_tok}")
    return errors


def apply_defaults(config: dict) -> dict:
    result = dict(config)
    for key, default in OPTIONAL_KEYS.items():
        result.setdefault(key, default)
    return result
