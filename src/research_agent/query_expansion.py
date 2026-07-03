from __future__ import annotations

import re

_SYNONYMS: dict[str, list[str]] = {
    "ai": ["artificial intelligence", "machine intelligence"],
    "ml": ["machine learning"],
    "nlp": ["natural language processing"],
    "llm": ["large language model", "language model"],
    "rag": ["retrieval augmented generation", "retrieval-augmented generation"],
    "fast": ["quick", "rapid", "swift"],
    "big": ["large", "huge", "massive"],
    "use": ["utilize", "employ", "leverage"],
}


def expand_query_with_synonyms(query: str, max_expansions: int = 3) -> list[str]:
    words = re.findall(r"\b\w+\b", query.lower())
    expansions = [query]
    for word in words:
        if word in _SYNONYMS and len(expansions) < max_expansions + 1:
            for synonym in _SYNONYMS[word]:
                expanded = re.sub(
                    r"\b" + re.escape(word) + r"\b", synonym, query, flags=re.IGNORECASE
                )
                if expanded != query and len(expansions) <= max_expansions:
                    expansions.append(expanded)
    return expansions


def add_related_terms(query: str) -> str:
    terms = []
    if re.search(r"\bRAG\b", query, re.I):
        terms.extend(["retrieval", "vector store", "embeddings"])
    if re.search(r"\bLangGraph\b", query, re.I):
        terms.extend(["stateful", "graph", "workflow"])
    if re.search(r"\bLLM\b", query, re.I):
        terms.extend(["language model", "transformer"])
    if not terms:
        return query
    return query + " " + " ".join(terms)


def deduplicate_queries(queries: list[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for q in queries:
        normalized = re.sub(r"\s+", " ", q.strip().lower())
        if normalized not in seen:
            seen.add(normalized)
            result.append(q)
    return result
