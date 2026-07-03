from __future__ import annotations

from research_agent.markdown_utils import strip_markdown, to_html


def test_to_html_header():
    result = to_html("# Title")
    assert "<h1>Title</h1>" in result


def test_to_html_bold():
    result = to_html("**bold text**")
    assert "<strong>bold text</strong>" in result


def test_to_html_code():
    result = to_html("`code snippet`")
    assert "<code>code snippet</code>" in result


def test_strip_markdown_removes_headers():
    result = strip_markdown("# Title\nsome text")
    assert "Title" in result
    assert "#" not in result


def test_strip_markdown_removes_bold():
    result = strip_markdown("**bold** and *italic*")
    assert "bold" in result and "italic" in result
    assert "*" not in result
