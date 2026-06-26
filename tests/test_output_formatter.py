from __future__ import annotations
import json
from research_agent.output_formatter import format_output, OutputFormat


SAMPLE = {
    "title": "AI Research Report",
    "summary": "This report covers advances in AI.",
    "sections": [{"heading": "Methods", "content": "We used transformer models."}],
    "citations": [{"source": "LeCun 2022"}],
}


def test_markdown_output():
    out = format_output(SAMPLE, OutputFormat.MARKDOWN)
    assert "# AI Research Report" in out and "## Methods" in out


def test_json_output():
    out = format_output(SAMPLE, OutputFormat.JSON)
    parsed = json.loads(out)
    assert parsed["title"] == "AI Research Report"


def test_plain_output():
    out = format_output(SAMPLE, OutputFormat.PLAIN)
    assert "AI Research Report" in out and "Methods" in out


def test_html_output():
    out = format_output(SAMPLE, OutputFormat.HTML)
    assert "<h1>" in out and "<h2>Methods</h2>" in out


def test_bullet_output():
    out = format_output(SAMPLE, OutputFormat.BULLET)
    assert "Summary:" in out


def test_format_string_arg():
    out = format_output(SAMPLE, "markdown")
    assert "# AI Research Report" in out
