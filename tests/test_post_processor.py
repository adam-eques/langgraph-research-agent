from __future__ import annotations

from langchain_core.documents import Document

from research_agent.rag.post_processor import deduplicate, filter_by_score, sort_by_score


def _doc(content: str, score: float = 1.0) -> Document:
    return Document(page_content=content, metadata={"rerank_score": score})


def test_deduplicate_removes_exact_duplicates():
    docs = [_doc("hello world"), _doc("hello world"), _doc("different content")]
    result = deduplicate(docs)
    assert len(result) == 2


def test_deduplicate_keeps_unique():
    docs = [_doc("document one"), _doc("document two"), _doc("document three")]
    result = deduplicate(docs)
    assert len(result) == 3


def test_deduplicate_empty():
    assert deduplicate([]) == []


def test_filter_by_score_removes_low():
    docs = [_doc("a", 0.9), _doc("b", 0.3), _doc("c", 0.7)]
    result = filter_by_score(docs, min_score=0.5)
    assert len(result) == 2


def test_filter_by_score_no_threshold():
    docs = [_doc("a", 0.1), _doc("b", 0.2)]
    assert len(filter_by_score(docs, min_score=0.0)) == 2


def test_sort_by_score_descending():
    docs = [_doc("a", 0.5), _doc("b", 0.9), _doc("c", 0.1)]
    sorted_docs = sort_by_score(docs)
    scores = [float(d.metadata["rerank_score"]) for d in sorted_docs]
    assert scores == sorted(scores, reverse=True)
