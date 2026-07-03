"""Report exporter — converts research output to Markdown, HTML, PDF, and JSON."""

from __future__ import annotations

import json
import logging
import textwrap
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      max-width: 860px;
      margin: 2rem auto;
      padding: 0 1.5rem;
      line-height: 1.7;
      color: #1a1a2e;
      background: #f9f9fb;
    }}
    h1, h2, h3 {{ color: #16213e; }}
    h1 {{ border-bottom: 2px solid #0f3460; padding-bottom: .4rem; }}
    blockquote {{
      border-left: 4px solid #0f3460;
      margin: 0;
      padding: .5rem 1rem;
      background: #eaf0fb;
      border-radius: 0 .25rem .25rem 0;
    }}
    .citation {{
      font-size: .85rem;
      color: #555;
      background: #eee;
      padding: .25rem .5rem;
      border-radius: .2rem;
      margin: .2rem 0;
      display: block;
    }}
    .meta {{
      font-size: .8rem;
      color: #888;
      margin-bottom: 1.5rem;
    }}
    pre {{ background: #222; color: #f8f8f2; padding: 1rem; border-radius: .3rem; overflow-x: auto; }}
    code {{ font-family: "JetBrains Mono", "Fira Code", monospace; font-size: .9em; }}
  </style>
</head>
<body>
{body}
</body>
</html>
"""


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")


class ReportExporter:
    """Converts a research result dict to various output formats.

    A *result dict* is the output of the research pipeline and must contain
    at least ``query`` and ``answer`` keys.  Optional keys:
    ``research_notes``, ``citations``, ``fact_check_results``.

    Example
    -------
    >>> exporter = ReportExporter()
    >>> md = exporter.to_markdown(result)
    >>> html = exporter.to_html(result)
    >>> exporter.to_pdf(result, "report.pdf")
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @staticmethod
    def to_markdown(result: dict[str, Any]) -> str:
        """Format the research result as a Markdown document.

        Parameters
        ----------
        result:
            Research pipeline output dict.

        Returns
        -------
        str
            UTF-8 Markdown string.
        """
        query = result.get("query", "Research Report")
        answer = result.get("answer", "*(no answer)*")
        notes: list[str] = result.get("research_notes", [])
        citations: list[dict[str, Any]] = result.get("citations", [])
        generated_at = _now_iso()

        lines = [
            "# Research Report",
            "",
            f"**Query:** {query}",
            f"**Generated:** {generated_at}",
            "",
            "---",
            "",
            "## Answer",
            "",
            answer,
        ]

        if citations:
            lines += ["", "---", "", "## Sources"]
            for i, cite in enumerate(citations, 1):
                source = cite.get("source", "unknown")
                excerpt = cite.get("excerpt", "")
                relevance = cite.get("relevance", "")
                lines.append(f"**[{i}]** `{source}`")
                if excerpt:
                    lines.append(f"> {excerpt[:200].strip()}")
                if relevance:
                    lines.append(f"*Relevance: {relevance}*")
                lines.append("")

        if notes:
            lines += ["", "---", "", "## Research Notes", ""]
            for note in notes:
                lines.append(f"- {note}")

        return "\n".join(lines)

    @staticmethod
    def to_html(result: dict[str, Any]) -> str:
        """Format the research result as a self-contained HTML page.

        Converts the Markdown output to HTML using a simple ``<pre>``-based
        formatter for portability (avoids requiring markdown2 or mistune).

        Parameters
        ----------
        result:
            Research pipeline output dict.

        Returns
        -------
        str
            Full HTML document as a string.
        """
        try:
            import markdown as _md  # type: ignore[import-untyped]

            md_text = ReportExporter.to_markdown(result)
            body_html = _md.markdown(
                md_text,
                extensions=["fenced_code", "tables", "nl2br"],
            )
        except ImportError:
            # Fallback: wrap markdown in <pre> for readable plain text
            md_text = ReportExporter.to_markdown(result)
            escaped = md_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            body_html = f"<pre style='white-space:pre-wrap'>{escaped}</pre>"

        query = result.get("query", "Research Report")
        title = f"Research: {query[:80]}"
        return _HTML_TEMPLATE.format(title=title, body=body_html)

    @staticmethod
    def to_pdf(result: dict[str, Any], output_path: str) -> None:
        """Save the research result as a PDF file.

        Requires ``fpdf2`` (``pip install fpdf2``).  The content is the
        Markdown-formatted report rendered as plain text inside the PDF.

        Parameters
        ----------
        result:
            Research pipeline output dict.
        output_path:
            Filesystem path where the PDF should be saved.

        Raises
        ------
        ImportError
            If ``fpdf2`` is not installed.
        """
        try:
            from fpdf import FPDF  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "fpdf2 is required for PDF export. Install it with: pip install fpdf2"
            ) from exc

        md_text = ReportExporter.to_markdown(result)
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)

        for line in md_text.splitlines():
            # Basic heading detection
            if line.startswith("# "):
                pdf.set_font("Helvetica", style="B", size=16)
                pdf.multi_cell(0, 8, line[2:])
                pdf.set_font("Helvetica", size=10)
            elif line.startswith("## "):
                pdf.set_font("Helvetica", style="B", size=13)
                pdf.multi_cell(0, 7, line[3:])
                pdf.set_font("Helvetica", size=10)
            elif line.startswith("### "):
                pdf.set_font("Helvetica", style="B", size=11)
                pdf.multi_cell(0, 6, line[4:])
                pdf.set_font("Helvetica", size=10)
            elif line.startswith("---"):
                pdf.ln(2)
                pdf.set_draw_color(100, 100, 100)
                pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 170, pdf.get_y())
                pdf.ln(2)
            elif line.startswith("> "):
                pdf.set_font("Helvetica", style="I", size=9)
                pdf.multi_cell(0, 5, line[2:])
                pdf.set_font("Helvetica", size=10)
            else:
                # Wrap long lines
                wrapped = textwrap.fill(line, width=100) if len(line) > 100 else line
                pdf.multi_cell(0, 5, wrapped)

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(output))
        logger.info("PDF report saved to %s", output)

    @staticmethod
    def to_json(result: dict[str, Any]) -> str:
        """Return a clean JSON representation of the research result.

        Strips any non-serialisable objects (LangChain message objects, etc.)
        and formats the output with 2-space indentation.

        Parameters
        ----------
        result:
            Research pipeline output dict.

        Returns
        -------
        str
            JSON string.
        """
        clean: dict[str, Any] = {
            "query": result.get("query", ""),
            "answer": result.get("answer", ""),
            "research_notes": result.get("research_notes", []),
            "citations": result.get("citations", []),
            "generated_at": _now_iso(),
        }
        if "fact_check_results" in result:
            fc = result["fact_check_results"]
            if hasattr(fc, "model_dump"):
                clean["fact_check_results"] = fc.model_dump()
            else:
                clean["fact_check_results"] = fc

        return json.dumps(clean, indent=2, default=str)
