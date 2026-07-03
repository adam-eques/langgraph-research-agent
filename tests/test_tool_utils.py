from __future__ import annotations

from research_agent.tool_utils import extract_tool_calls, format_tool_result, tool_call_to_dict


def test_format_tool_result_short():
    result = format_tool_result("search", "some results")
    assert "[search result]" in result
    assert "some results" in result


def test_format_tool_result_truncated():
    long = "x" * 3000
    result = format_tool_result("search", long, max_chars=100)
    assert "truncated" in result
    assert len(result) < 3100


def test_extract_tool_calls_from_list():
    content = [
        {"type": "text", "text": "thinking..."},
        {"type": "tool_use", "name": "search", "id": "1", "input": {"q": "ai"}},
    ]
    calls = extract_tool_calls(content)
    assert len(calls) == 1
    assert calls[0]["name"] == "search"


def test_extract_tool_calls_from_string():
    assert extract_tool_calls("just text") == []


def test_tool_call_to_dict():
    call = {"type": "tool_use", "id": "abc", "name": "fetch", "input": {"url": "x"}}
    result = tool_call_to_dict(call)
    assert result["name"] == "fetch"
    assert result["id"] == "abc"
