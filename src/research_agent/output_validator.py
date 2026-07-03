from __future__ import annotations

import json
import logging
import re
from typing import Any, cast

logger = logging.getLogger(__name__)


def extract_and_parse_json(text: str) -> dict | None:
    match = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    raw = match.group(1).strip() if match else text.strip()
    try:
        return cast("dict | None", json.loads(raw))
    except json.JSONDecodeError as e:
        logger.debug("JSON parse failed: %s", e)
        return None


def validate_required_keys(data: dict, required: list[str]) -> list[str]:
    return [k for k in required if k not in data]


def coerce_to_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]
