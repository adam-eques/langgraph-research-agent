from __future__ import annotations

from research_agent.node_registry import NodeRegistry


def dummy_fn():
    return "ok"


def test_register_and_get():
    reg = NodeRegistry()
    reg.register("retrieve", dummy_fn, "Fetch documents")
    assert reg.get("retrieve") is dummy_fn


def test_list_names_sorted():
    reg = NodeRegistry()
    reg.register("b", dummy_fn)
    reg.register("a", dummy_fn)
    assert reg.list_names() == ["a", "b"]


def test_by_tag():
    reg = NodeRegistry()
    reg.register("plan", dummy_fn, tags=["core"])
    reg.register("retrieve", dummy_fn, tags=["core", "rag"])
    assert "retrieve" in reg.by_tag("rag")


def test_unregister():
    reg = NodeRegistry()
    reg.register("x", dummy_fn)
    assert reg.unregister("x") is True and reg.get("x") is None


def test_describe():
    reg = NodeRegistry()
    reg.register("analyse", dummy_fn, description="Analyse results")
    assert reg.describe("analyse") == "Analyse results"
