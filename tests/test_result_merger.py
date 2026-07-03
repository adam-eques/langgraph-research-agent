from __future__ import annotations

from research_agent.rag.result_merger import MergedResult, deduplicate_results, merge_results


def test_merge_single_source():
    results = [{"doc_id": "a", "content": "text", "score": 0.9}]
    merged = merge_results([results])
    assert len(merged) == 1 and merged[0].doc_id == "a"


def test_merge_deduplicates_across_sources():
    s1 = [{"doc_id": "a", "content": "text", "score": 0.8}]
    s2 = [{"doc_id": "a", "content": "text", "score": 0.6}]
    merged = merge_results([s1, s2])
    assert len(merged) == 1


def test_merge_score_agg_max():
    s1 = [{"doc_id": "x", "content": "c", "score": 0.9}]
    s2 = [{"doc_id": "x", "content": "c", "score": 0.3}]
    merged = merge_results([s1, s2], score_agg="max")
    assert merged[0].score == 1.0


def test_merge_top_k():
    source = [{"doc_id": str(i), "content": "c", "score": i * 0.1} for i in range(20)]
    merged = merge_results([source], top_k=5)
    assert len(merged) <= 5


def test_deduplicate_results():
    results = [
        {"content": "The quick brown fox jumps over the lazy dog."},
        {"content": "The quick brown fox jumps over the lazy dog."},
        {"content": "An entirely different document about science."},
    ]
    unique = deduplicate_results(results, threshold=0.9)
    assert len(unique) == 2


def test_merged_result_to_dict():
    r = MergedResult("d1", "content text", 0.75, ["0", "1"])
    d = r.to_dict()
    assert d["doc_id"] == "d1" and d["score"] == 0.75
