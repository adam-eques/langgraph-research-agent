from __future__ import annotations

from research_agent.document_store import DocumentStore, StoredDocument


def test_add_and_get():
    store = DocumentStore()
    doc = store.add("Hello world", tags=["greeting"])
    assert store.get(doc.doc_id) is doc


def test_delete():
    store = DocumentStore()
    doc = store.add("temp content")
    assert store.delete(doc.doc_id) is True
    assert store.get(doc.doc_id) is None
    assert store.count == 0


def test_find_by_tag():
    store = DocumentStore()
    store.add("doc A", tags=["ml", "ai"])
    store.add("doc B", tags=["nlp"])
    store.add("doc C", tags=["ml"])
    result = store.find_by_tag("ml")
    assert len(result) == 2


def test_search_content():
    store = DocumentStore()
    store.add("LangGraph is a graph framework.")
    store.add("Python is great for data science.")
    hits = store.search_content("LangGraph")
    assert len(hits) == 1 and "LangGraph" in hits[0].content


def test_update_metadata():
    store = DocumentStore()
    doc = store.add("test content")
    ok = store.update_metadata(doc.doc_id, {"author": "alice"})
    assert ok and store.get(doc.doc_id).metadata["author"] == "alice"


def test_to_dict():
    doc = StoredDocument("id1", "text", metadata={}, tags=["x"])
    d = doc.to_dict()
    assert d["length"] == 4 and "tags" in d
