from __future__ import annotations

from research_agent.rag.index_manager import IndexManager


def test_create_and_exists():
    mgr = IndexManager()
    mgr.create("test_col")
    assert mgr.exists("test_col") is True


def test_drop_collection():
    mgr = IndexManager()
    mgr.create("col1")
    assert mgr.drop("col1") is True and not mgr.exists("col1")


def test_list_collections():
    mgr = IndexManager()
    mgr.create("b_col")
    mgr.create("a_col")
    assert mgr.list_collections() == ["a_col", "b_col"]


def test_stats_and_increment():
    mgr = IndexManager()
    mgr.create("col")
    mgr.increment_doc_count("col", 5)
    assert mgr.stats("col")["doc_count"] == 5
