from __future__ import annotations

import json
from enum import StrEnum


class OutputFormat(StrEnum):
    MARKDOWN = "markdown"
    JSON = "json"
    PLAIN = "plain"
    HTML = "html"
    BULLET = "bullet"


def _to_markdown(data: dict) -> str:
    lines = []
    if "title" in data:
        lines.append(f"# {data['title']}\n")
    if "summary" in data:
        lines.append(f"{data['summary']}\n")
    if "sections" in data:
        for section in data["sections"]:
            heading = section.get("heading", "")
            content = section.get("content", "")
            lines.append(f"\n## {heading}\n\n{content}")
    if "citations" in data:
        lines.append("\n## References\n")
        for i, c in enumerate(data["citations"], 1):
            lines.append(f"{i}. {c.get('source', 'Unknown')}")
    return "\n".join(lines)


def _to_plain(data: dict) -> str:
    parts = []
    if "title" in data:
        parts.append(data["title"])
    if "summary" in data:
        parts.append(data["summary"])
    if "sections" in data:
        for s in data["sections"]:
            parts.append(s.get("heading", ""))
            parts.append(s.get("content", ""))
    return "\n\n".join(parts)


def _to_bullet(data: dict) -> str:
    bullets = []
    if "summary" in data:
        bullets.append(f"Summary: {data['summary']}")
    if "sections" in data:
        for s in data["sections"]:
            bullets.append(f"- {s.get('heading', '')}: {s.get('content', '')[:80]}")
    return "\n".join(bullets)


def _to_html(data: dict) -> str:
    parts = []
    if "title" in data:
        parts.append(f"<h1>{data['title']}</h1>")
    if "summary" in data:
        parts.append(f"<p>{data['summary']}</p>")
    if "sections" in data:
        for s in data["sections"]:
            parts.append(f"<h2>{s.get('heading', '')}</h2>")
            parts.append(f"<p>{s.get('content', '')}</p>")
    return "\n".join(parts)


def format_output(data: dict, fmt: OutputFormat | str = OutputFormat.MARKDOWN) -> str:
    f = OutputFormat(fmt) if isinstance(fmt, str) else fmt
    if f == OutputFormat.MARKDOWN:
        return _to_markdown(data)
    if f == OutputFormat.JSON:
        return json.dumps(data, indent=2, ensure_ascii=False)
    if f == OutputFormat.PLAIN:
        return _to_plain(data)
    if f == OutputFormat.HTML:
        return _to_html(data)
    if f == OutputFormat.BULLET:
        return _to_bullet(data)
    return str(data)
