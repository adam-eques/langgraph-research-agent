from __future__ import annotations

from research_agent.lang_detect import detect_language, is_english


def test_english_detected():
    assert detect_language("The quick brown fox jumps over the lazy dog") == "en"


def test_cyrillic_detected():
    assert detect_language("Привет мир тест на русском языке") == "ru"


def test_is_english_true():
    assert is_english("Hello world") is True


def test_is_english_false():
    assert is_english("Привет мир это проверка текста") is False
