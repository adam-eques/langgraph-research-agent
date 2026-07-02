from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def format_tool_result(tool_name: str, result: Any, max_chars: int = 2000) -> str:
    """Format a tool call result for inclusion in agent context."""
    result_str = str(result)
    if len(result_str) > max_chars:
        logger.debug("Tool result from %s truncated from %d chars", tool_name, len(result_str))
        result_str = result_str[:max_chars] + f"\n...[truncated, {len(result_str)} total chars]"
    return f"[{tool_name} result]\n{result_str}"


def extract_tool_calls(message_content: Any) -> list[dict]:
    """Extract tool call blocks from a LangChain message content."""
    if isinstance(message_content, list):
        return [
            block
            for block in message_content
            if isinstance(block, dict) and block.get("type") == "tool_use"
        ]
    return []


def tool_call_to_dict(call: dict) -> dict:
    """Normalize a tool call block to a flat dict."""
    return {
        "id": call.get("id", ""),
        "name": call.get("name", ""),
        "input": call.get("input", {}),
    }
