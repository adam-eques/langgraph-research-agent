from __future__ import annotations

from research_agent.query_deduplicator import (
    deduplicate,
    deduplicate_exact,
    deduplicate_fuzzy,
)


def test_exact_dedup_removes_duplicates():
    queries = ["What is AI?", "What is AI?", "What is machine learning?"]
    result = deduplicate_exact(queries)
    assert result.deduplicated_count == 2
    assert 1 in result.removed_indices


def test_exact_dedup_case_insensitive():
    queries = ["What is AI?", "what is ai?"]
    result = deduplicate_exact(queries)
    assert result.deduplicated_count == 1


def test_exact_dedup_no_duplicates():
    queries = ["query one", "query two", "query three"]
    result = deduplicate_exact(queries)
    assert result.deduplicated_count == 3 and len(result.removed_indices) == 0


def test_fuzzy_dedup_similar_queries():
    queries = [
        "How does machine learning work?",
        "How does machine learning function?",
        "Explain quantum computing in detail.",
    ]
    result = deduplicate_fuzzy(queries, similarity_threshold=0.6)
    assert result.deduplicated_count == 2


def test_deduplicate_exact_shortcut():
    queries = ["a", "b", "a"]
    unique = deduplicate(queries)
    assert len(unique) == 2


def test_reduction_pct():
    queries = ["q", "q", "q", "other"]
    result = deduplicate_exact(queries)
    assert result.reduction_pct() > 0
