from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


def remove_filler_words(query: str) -> str:
    fillers = [
        "please",
        "can you",
        "could you",
        "tell me",
        "i want to know",
        "what are",
        "what is the",
        "i need",
        "give me",
    ]
    q = query.strip()
    # Repeatedly strip leading fillers until none match, so stacked fillers
    # (e.g. "Please tell me ...") are all removed regardless of ordering.
    changed = True
    while changed:
        changed = False
        for filler in fillers:
            stripped = re.sub(rf"(?i)^{re.escape(filler)}\s*", "", q)
            if stripped != q:
                q = stripped
                changed = True
    return q.strip()


def normalize_query(query: str) -> str:
    query = query.strip()
    query = re.sub(r"\s+", " ", query)
    if query and query[-1] not in ".?!":
        query = query + "?"
    return query


def rewrite_for_search(query: str) -> str:
    q = remove_filler_words(query)
    q = re.sub(r"(?i)\bplease\b", "", q)
    q = re.sub(r"[?!.]+$", "", q).strip()
    return q
