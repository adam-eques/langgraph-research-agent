from __future__ import annotations

from research_agent.output_buffer import OutputBuffer


def test_push_no_flush_until_chunk():
    buf = OutputBuffer(chunk_size=3)
    assert buf.push("a") is None
    assert buf.push("b") is None
    result = buf.push("c")
    assert result == "abc"


def test_flush_partial():
    buf = OutputBuffer(chunk_size=10)
    buf.push("hello")
    result = buf.flush()
    assert result == "hello"
    assert len(buf) == 0


def test_len():
    buf = OutputBuffer(chunk_size=5)
    buf.push("x")
    buf.push("y")
    assert len(buf) == 2
