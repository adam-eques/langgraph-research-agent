from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_system_prompt(
    role: str,
    task_description: str,
    constraints: list[str] | None = None,
    output_format: str | None = None,
) -> str:
    """Construct a structured system prompt from components."""
    parts = [f"You are {role}.", "", task_description]
    if constraints:
        parts += ["", "Constraints:"] + [f"- {c}" for c in constraints]
    if output_format:
        parts += ["", "Output format:", output_format]
    return "\n".join(parts)


def researcher_system_prompt(additional_context: str = "") -> str:
    constraints = [
        "Use only information from provided tools.",
        "Cite sources explicitly.",
        "Do not fabricate data.",
    ]
    task = "Your task is to perform web research and gather relevant information to answer the query."
    prompt = build_system_prompt("a research assistant", task, constraints=constraints)
    if additional_context:
        prompt += f"\n\nAdditional context:\n{additional_context}"
    return prompt


def analyst_system_prompt() -> str:
    task = "Your task is to analyze research notes and produce a structured analysis."
    output_fmt = "Return a JSON object with: summary, key_findings (list), gaps (list), confidence (0-1)."
    return build_system_prompt("an expert analyst", task, output_format=output_fmt)
