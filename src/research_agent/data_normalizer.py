from __future__ import annotations

import re
from typing import Any


def normalize_string(value: str) -> str:
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return default


def normalize_boolean(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in {"true", "yes", "1", "on", "enabled"}
    return bool(value)


def normalize_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        if "," in value:
            return [v.strip() for v in value.split(",") if v.strip()]
        return [value.strip()] if value.strip() else []
    return list(value) if hasattr(value, "__iter__") else [value]


def normalize_record(record: dict[str, Any], schema: dict[str, str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, dtype in schema.items():
        raw = record.get(key)
        if dtype == "str":
            result[key] = normalize_string(str(raw)) if raw is not None else ""
        elif dtype == "float":
            result[key] = normalize_number(raw)
        elif dtype == "bool":
            result[key] = normalize_boolean(raw)
        elif dtype == "list":
            result[key] = normalize_list(raw)
        else:
            result[key] = raw
    return result
