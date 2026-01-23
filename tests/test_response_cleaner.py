from __future__ import annotations

from research_agent.response_cleaner import fix_spacing, clean_llm_output


def test_fix_spacing_collapses_spaces():
    result = fix_spacing("hello   world")
    assert result == "hello world"


def test_fix_spacing_collapses_newlines():
    result = fix_spacing("line1\n\n\n\nline2")
    assert "\n\n\n" not in result


def test_clean_llm_output_strips_prefix():
    result = clean_llm_output("AI: Here is the answer.")
    assert not result.startswith("AI:")


def test_clean_llm_output_strips_assistant():
    result = clean_llm_output("assistant: Here is the answer to your query.")
    assert not result.lower().startswith("assistant")
