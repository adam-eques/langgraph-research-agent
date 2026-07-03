from __future__ import annotations

from research_agent.search_ranker import RankedSearchResult, SearchResult, rank_search_results


def make_result(doc_id, content, score=0.5, year=None):
    meta = {"year": year} if year else {}
    return SearchResult(doc_id=doc_id, content=content, base_score=score, metadata=meta)


def test_rank_returns_all_results():
    results = [make_result("a", "text one"), make_result("b", "text two")]
    ranked = rank_search_results(results, "text")
    assert len(ranked) == 2


def test_rank_assigns_rank_field():
    results = [make_result("a", "hello"), make_result("b", "world")]
    ranked = rank_search_results(results, "hello")
    assert sorted(r.rank for r in ranked) == [1, 2]


def test_coverage_boosts_relevant_doc():
    results = [
        make_result("relevant", "machine learning neural networks deep", score=0.5),
        make_result("irrelevant", "today is sunny and warm outside nice", score=0.5),
    ]
    ranked = rank_search_results(results, "machine learning neural")
    assert ranked[0].doc_id == "relevant"


def test_freshness_boosts_recent():
    results = [
        make_result("old", "same content here", score=0.5, year=2010),
        make_result("new", "same content here", score=0.5, year=2025),
    ]
    ranked = rank_search_results(results, "content")
    assert ranked[0].doc_id == "new"


def test_to_dict_has_signals():
    r = RankedSearchResult("d1", "content", 0.7, 1, signals={"base": 0.5, "coverage": 0.8})
    d = r.to_dict()
    assert "signals" in d and d["rank"] == 1


def test_empty_results():
    assert rank_search_results([], "query") == []
