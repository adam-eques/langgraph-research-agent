from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def validate_research_state(state: dict) -> list[str]:
    """Return a list of validation errors for a ResearchState dict."""
    errors = []
    if not state.get("query"):
        errors.append("query is required")
    if not isinstance(state.get("research_notes", []), list):
        errors.append("research_notes must be a list")
    if not isinstance(state.get("citations", []), list):
        errors.append("citations must be a list")
    for i, c in enumerate(state.get("citations", [])):
        if not isinstance(c, dict):
            errors.append(f"citation[{i}] must be a dict")
        elif "source" not in c:
            errors.append(f"citation[{i}] missing 'source' key")
    return errors


def assert_state_valid(state: dict) -> None:
    errors = validate_research_state(state)
    if errors:
        raise ValueError(f"Invalid ResearchState: {'; '.join(errors)}")
