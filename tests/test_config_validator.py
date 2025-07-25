from __future__ import annotations
from research_agent.config_validator import validate_config, apply_defaults

def test_missing_api_key():
    errors = validate_config({})
    assert any("anthropic_api_key" in e for e in errors)

def test_valid_config():
    errors = validate_config({"anthropic_api_key": "sk-test", "temperature": 0.7})
    assert errors == []

def test_invalid_temperature():
    errors = validate_config({"anthropic_api_key": "sk-test", "temperature": 5.0})
    assert any("temperature" in e for e in errors)

def test_apply_defaults():
    config = apply_defaults({"anthropic_api_key": "sk-test"})
    assert "model" in config
    assert config["temperature"] == 0.0
