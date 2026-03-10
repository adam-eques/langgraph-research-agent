from __future__ import annotations
from research_agent.query_expansion import (
    expand_query_with_synonyms, add_related_terms, deduplicate_queries,
)


def test_expand_synonym():
    expansions = expand_query_with_synonyms("How does AI work?")
    assert len(expansions) >= 1


def test_no_expansion_if_no_synonym():
    result = expand_query_with_synonyms("What is a database?")
    assert result[0] == "What is a database?"


def test_add_rag_terms():
    result = add_related_terms("Explain RAG pipeline")
    assert "retrieval" in result.lower()


def test_deduplicate():
    queries = ["What is AI?", "what is ai?", "What is ML?"]
    unique = deduplicate_queries(queries)
    assert len(unique) == 2
