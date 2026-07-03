from __future__ import annotations

from research_agent.doc_registry import DocumentRegistry


def test_register_and_is_registered(tmp_path):
    reg = DocumentRegistry(registry_path=str(tmp_path / "reg.json"))
    reg.register("/fake/path.pdf", "research_docs")
    assert reg.is_registered("/fake/path.pdf") is True


def test_not_registered_initially(tmp_path):
    reg = DocumentRegistry(registry_path=str(tmp_path / "reg.json"))
    assert reg.is_registered("/nonexistent.pdf") is False


def test_all_docs_returns_list(tmp_path):
    reg = DocumentRegistry(registry_path=str(tmp_path / "reg.json"))
    reg.register("/a.pdf", "col1")
    reg.register("/b.pdf", "col2")
    assert len(reg.all_docs()) == 2


def test_register_returns_key(tmp_path):
    reg = DocumentRegistry(registry_path=str(tmp_path / "reg.json"))
    key = reg.register("/a.pdf", "docs")
    assert len(key) == 16
