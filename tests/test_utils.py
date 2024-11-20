from __future__ import annotations

import pytest

from research_agent.utils import hash_query, truncate, clean_whitespace, chunk_list, retry


def test_hash_query_stable():
    assert hash_query("hello") == hash_query("hello")


def test_hash_query_case_insensitive():
    assert hash_query("Hello World") == hash_query("hello world")


def test_hash_query_strips_whitespace():
    assert hash_query("  hello  ") == hash_query("hello")


def test_truncate_short_string():
    assert truncate("hi", 100) == "hi"


def test_truncate_long_string():
    result = truncate("a" * 200, 50)
    assert len(result) == 50
    assert result.endswith("...")


def test_clean_whitespace_collapses_spaces():
    assert clean_whitespace("  hello   world  ") == "hello world"


def test_clean_whitespace_handles_newlines():
    assert clean_whitespace("hello\n\nworld") == "hello world"


def test_chunk_list_even():
    result = chunk_list([1, 2, 3, 4], 2)
    assert result == [[1, 2], [3, 4]]


def test_chunk_list_uneven():
    result = chunk_list([1, 2, 3], 2)
    assert result == [[1, 2], [3]]


def test_chunk_list_empty():
    assert chunk_list([], 3) == []


def test_retry_succeeds_first_attempt():
    calls = []

    @retry(max_attempts=3)
    def fn():
        calls.append(1)
        return "ok"

    assert fn() == "ok"
    assert len(calls) == 1


def test_retry_retries_on_failure():
    calls = []

    @retry(max_attempts=3, delay=0)
    def fn():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("fail")
        return "ok"

    assert fn() == "ok"
    assert len(calls) == 3


def test_retry_raises_after_all_attempts():
    @retry(max_attempts=2, delay=0)
    def fn():
        raise RuntimeError("always fails")

    with pytest.raises(RuntimeError):
        fn()
