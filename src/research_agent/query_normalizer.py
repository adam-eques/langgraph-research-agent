from __future__ import annotations

import re
import unicodedata


def unicode_normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def remove_punctuation_edges(text: str) -> str:
    return text.rstrip(".,;:!?\"'()[]{}\\/-")


def lowercase_unless_acronym(text: str) -> str:
    words = []
    for word in text.split():
        words.append(word if word.isupper() and len(word) > 2 else word.lower())
    return " ".join(words)


def normalize_query(text: str) -> str:
    text = unicode_normalize(text)
    text = collapse_whitespace(text)
    text = remove_punctuation_edges(text)
    text = lowercase_unless_acronym(text)
    return text


def expand_contractions(text: str) -> str:
    contractions = {
        "can't": "cannot",
        "won't": "will not",
        "don't": "do not",
        "doesn't": "does not",
        "isn't": "is not",
        "aren't": "are not",
        "wasn't": "was not",
        "weren't": "were not",
        "it's": "it is",
        "i'm": "i am",
        "i've": "i have",
        "i'll": "i will",
        "what's": "what is",
        "that's": "that is",
    }
    for k, v in contractions.items():
        text = re.sub(re.escape(k), v, text, flags=re.IGNORECASE)
    return text
