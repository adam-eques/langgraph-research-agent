from __future__ import annotations

import pytest
from datetime import datetime
from langchain_core.documents import Document

from research_agent.rag.metadata_filter import MetadataFilter, filter_by_date


def _doc(**meta) -> Document:
    return Document(page_content="test content", metadata=meta)


def test_filter_eq():
    docs = [_doc(source="a.pdf"), _doc(source="b.pdf"), _doc(source="a.pdf")]
    result = MetadataFilter().where("source", "eq", "a.pdf").apply(docs)
    assert len(result) == 2


def test_filter_ne():
    docs = [_doc(type="report"), _doc(type="memo"), _doc(type="report")]
    result = MetadataFilter().where("type", "ne", "memo").apply(docs)
    assert len(result) == 2


def test_filter_gt():
    docs = [_doc(page=1), _doc(page=5), _doc(page=10)]
    result = MetadataFilter().where("page", "gt", 4).apply(docs)
    assert len(result) == 2


def test_filter_contains():
    docs = [_doc(filename="report_2024.pdf"), _doc(filename="memo.docx")]
    result = MetadataFilter().where("filename", "contains", "2024").apply(docs)
    assert len(result) == 1


def test_filter_in():
    docs = [_doc(source="a.pdf"), _doc(source="b.pdf"), _doc(source="c.pdf")]
    result = MetadataFilter().where("source", "in", ["a.pdf", "c.pdf"]).apply(docs)
    assert len(result) == 2


def test_filter_missing_field_excluded():
    docs = [_doc(source="a.pdf"), Document(page_content="no metadata")]
    result = MetadataFilter().where("source", "eq", "a.pdf").apply(docs)
    assert len(result) == 1


def test_filter_chained():
    docs = [
        _doc(source="a.pdf", page=5),
        _doc(source="a.pdf", page=1),
        _doc(source="b.pdf", page=5),
    ]
    result = MetadataFilter().where("source", "eq", "a.pdf").where("page", "gt", 3).apply(docs)
    assert len(result) == 1


def test_filter_by_date_after():
    docs = [
        _doc(created_at="2024-01-01"),
        _doc(created_at="2025-06-01"),
        _doc(created_at="2025-12-01"),
    ]
    result = filter_by_date(docs, after=datetime(2025, 1, 1))
    assert len(result) == 2


def test_filter_by_date_no_metadata_passes():
    docs = [Document(page_content="no date")]
    result = filter_by_date(docs, after=datetime(2025, 1, 1))
    assert len(result) == 1
