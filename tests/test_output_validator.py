from __future__ import annotations

from research_agent.output_validator import extract_and_parse_json, validate_required_keys, coerce_to_list


def test_extract_json_from_code_block():
    text = "Here is output:\n```json\n{\"key\": \"val\"}\n```"
    result = extract_and_parse_json(text)
    assert result == {"key": "val"}


def test_extract_raw_json():
    result = extract_and_parse_json('{"a": 1}')
    assert result["a"] == 1


def test_extract_invalid_json():
    assert extract_and_parse_json("not json") is None


def test_validate_required_keys():
    data = {"a": 1, "b": 2}
    missing = validate_required_keys(data, ["a", "c"])
    assert missing == ["c"]


def test_coerce_to_list():
    assert coerce_to_list(None) == []
    assert coerce_to_list("x") == ["x"]
    assert coerce_to_list([1, 2]) == [1, 2]
