from __future__ import annotations


def detect_language(text: str) -> str:
    cjk = sum(1 for c in text if "一" <= c <= "鿿")
    cyrillic = sum(1 for c in text if "Ѐ" <= c <= "ӿ")
    arabic = sum(1 for c in text if "؀" <= c <= "ۿ")
    total = max(len(text), 1)
    if cjk / total > 0.1:
        return "zh"
    if cyrillic / total > 0.1:
        return "ru"
    if arabic / total > 0.1:
        return "ar"
    return "en"


def is_english(text: str) -> bool:
    return detect_language(text) == "en"
