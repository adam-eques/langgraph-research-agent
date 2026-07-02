from __future__ import annotations

import pytest

from research_agent.rag.document_loader import detect_file_type, list_documents, load_text_file


def test_load_text_file(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_text("hello world")
    content = load_text_file(str(f))
    assert content == "hello world"


def test_load_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_text_file(str(tmp_path / "missing.txt"))


def test_detect_file_type():
    assert detect_file_type("report.pdf") == "pdf"
    assert detect_file_type("notes.md") == "markdown"
    assert detect_file_type("data.txt") == "text"


def test_list_documents(tmp_path):
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.md").write_text("b")
    (tmp_path / "c.jpg").write_text("c")
    docs = list_documents(str(tmp_path))
    assert len(docs) == 2
