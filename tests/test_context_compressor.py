from __future__ import annotations

from research_agent.context_compressor import ContextCompressor


def test_strip_boilerplate():
    comp = ContextCompressor()
    text = "Useful content here.\nCookie Policy applies.\nMore content."
    result = comp.strip_boilerplate(text)
    assert "Cookie Policy" not in result
    assert "Useful content" in result


def test_remove_duplicate_sentences():
    comp = ContextCompressor()
    text = "AI is growing. AI is growing. ML is important."
    result = comp.remove_duplicate_sentences(text)
    assert result.count("AI is growing") == 1


def test_compress_truncates():
    comp = ContextCompressor(max_chars=20)
    result = comp.compress("a" * 100)
    assert len(result) <= 30
    assert "[compressed]" in result


def test_compress_short_text():
    comp = ContextCompressor(max_chars=1000)
    text = "Short text."
    assert comp.compress(text) == text
