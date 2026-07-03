"""Example: run research and export the result in multiple formats."""

from __future__ import annotations

import sys
from pathlib import Path

from research_agent.export import ReportExporter
from research_agent.streaming import run


def main(query: str, output_dir: str = ".") -> None:
    out = Path(output_dir)
    out.mkdir(exist_ok=True)

    print(f"Researching: {query!r}")
    result = run(query)

    md_path = out / "report.md"
    md_path.write_text(ReportExporter.to_markdown(result))
    print(f"Markdown: {md_path}")

    html_path = out / "report.html"
    html_path.write_text(ReportExporter.to_html(result))
    print(f"HTML:     {html_path}")

    json_path = out / "report.json"
    json_path.write_text(ReportExporter.to_json(result))
    print(f"JSON:     {json_path}")

    pdf_path = str(out / "report.pdf")
    try:
        ReportExporter.to_pdf(result, pdf_path)
        print(f"PDF:      {pdf_path}")
    except Exception as exc:
        print(f"PDF skipped ({exc}) — install fpdf2 to enable")


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is retrieval-augmented generation?"
    main(q)
