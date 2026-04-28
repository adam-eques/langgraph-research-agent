from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_json_config(path: str) -> dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc


def load_env_config(prefix: str = "RESEARCH_") -> dict[str, str]:
    return {
        k[len(prefix):].lower(): v
        for k, v in os.environ.items()
        if k.startswith(prefix)
    }


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for cfg in configs:
        for k, v in cfg.items():
            if k in result and isinstance(result[k], dict) and isinstance(v, dict):
                result[k] = merge_configs(result[k], v)
            else:
                result[k] = v
    return result


def get_nested(config: dict, *keys: str, default: Any = None) -> Any:
    current = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def validate_required_keys_config(config: dict, required: list[str]) -> list[str]:
    return [k for k in required if k not in config]
