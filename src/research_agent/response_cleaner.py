from __future__ import annotations

import re


def remove_repetitive_phrases(text: str, min_repeat: int = 3) -> str:
    """Remove phrases repeated more than min_repeat times."""
    words = text.split()
    cleaned, i = [], 0
    while i < len(words):
        window = words[i : i + 4]
        phrase = " ".join(window)
        if text.count(phrase) >= min_repeat and len(window) > 1:
            i += len(window)
        else:
            cleaned.append(words[i])
            i += 1
    return " ".join(cleaned)


def fix_spacing(text: str) -> str:
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_llm_output(text: str) -> str:
    text = re.sub(r"^(assistant|AI|Claude):\s*", "", text, flags=re.IGNORECASE)
    text = fix_spacing(text)
    return text.strip()
