from __future__ import annotations

import json


def format_research_result(
    query: str,
    answer: str,
    citations: list[dict],
    notes: list[str],
    style: str = "markdown",
) -> str:
    if style == "json":
        return json.dumps(
            {
                "query": query,
                "answer": answer,
                "citations": citations,
                "research_notes": notes,
            },
            indent=2,
        )
    if style == "plain":
        parts = [f"Query: {query}", "", answer]
        if citations:
            parts += ["", "Sources:"] + [f"- {c.get('source', '?')}" for c in citations]
        return "\n".join(parts)
    # Default markdown
    parts = [f"## Research: {query}", "", answer]
    if citations:
        parts += ["", "### Sources"]
        for i, c in enumerate(citations, 1):
            parts.append(f"{i}. {c.get('source', '?')}")
    return "\n".join(parts)
