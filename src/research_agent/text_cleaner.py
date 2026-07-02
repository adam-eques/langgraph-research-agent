from __future__ import annotations

import re
import unicodedata


def remove_html_tags(text: str) -> str:
    # Collapse each run of adjacent tags into a single space so "</b></p>"
    # does not leave a double space.
    return re.sub(r"(?:<[^>]+>)+", " ", text)


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def remove_urls(text: str) -> str:
    return re.sub(r"https?://\S+|www\.\S+", "", text)


def remove_special_chars(text: str, keep_punctuation: bool = True) -> str:
    if keep_punctuation:
        return re.sub(r"[^\w\s.,;:!?\"'\-()\n]", "", text)
    return re.sub(r"[^\w\s]", "", text)


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def clean_scraped_text(
    text: str,
    remove_urls_flag: bool = True,
    remove_html: bool = True,
    normalize_unicode_flag: bool = False,
) -> str:
    if remove_html:
        text = remove_html_tags(text)
    if remove_urls_flag:
        text = remove_urls(text)
    text = normalize_whitespace(text)
    if normalize_unicode_flag:
        text = normalize_unicode(text)
    return text
