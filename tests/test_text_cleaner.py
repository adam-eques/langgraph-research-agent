from __future__ import annotations
from research_agent.text_cleaner import (
    remove_html_tags, normalize_whitespace, remove_urls, clean_scraped_text,
)


def test_remove_html_tags():
    assert remove_html_tags("<p>Hello <b>world</b></p>") == " Hello  world "


def test_normalize_whitespace():
    text = "Hello\n\n\n\nWorld   trailing  "
    assert normalize_whitespace(text) == "Hello\n\nWorld trailing"


def test_remove_urls():
    text = "Visit https://example.com for more info"
    assert "example.com" not in remove_urls(text)


def test_clean_scraped_text():
    raw = "<div>Check <a href='https://x.com'>this</a></div>"
    cleaned = clean_scraped_text(raw)
    assert "<" not in cleaned and "https" not in cleaned
