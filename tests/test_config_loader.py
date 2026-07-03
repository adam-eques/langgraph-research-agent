from __future__ import annotations

import json

import pytest

from research_agent.config_loader import (
    get_nested,
    load_json_config,
    merge_configs,
    validate_required_keys_config,
)


def test_load_json_config(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({"key": "value"}))
    result = load_json_config(str(cfg_file))
    assert result["key"] == "value"


def test_load_json_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_json_config(str(tmp_path / "missing.json"))


def test_merge_configs_deep():
    a = {"db": {"host": "localhost", "port": 5432}}
    b = {"db": {"port": 5433, "name": "research"}}
    merged = merge_configs(a, b)
    assert merged["db"]["host"] == "localhost" and merged["db"]["port"] == 5433


def test_get_nested():
    cfg = {"llm": {"model": "claude", "temp": 0.3}}
    assert get_nested(cfg, "llm", "model") == "claude"
    assert get_nested(cfg, "llm", "missing", default="x") == "x"


def test_validate_required():
    cfg = {"a": 1, "b": 2}
    missing = validate_required_keys_config(cfg, ["a", "b", "c"])
    assert missing == ["c"]
