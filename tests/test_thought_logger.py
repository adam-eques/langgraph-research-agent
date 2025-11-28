from __future__ import annotations

from research_agent.thought_logger import ThoughtLogger


def test_log_and_retrieve():
    tl = ThoughtLogger()
    tl.log("researcher", "I should search for papers on AI.", step=1)
    thoughts = tl.for_agent("researcher")
    assert len(thoughts) == 1
    assert "papers on AI" in thoughts[0]["thought"]


def test_for_agent_filters():
    tl = ThoughtLogger()
    tl.log("researcher", "thought A")
    tl.log("analyst", "thought B")
    assert len(tl.for_agent("researcher")) == 1
    assert len(tl.for_agent("analyst")) == 1


def test_clear():
    tl = ThoughtLogger()
    tl.log("a", "thought")
    tl.clear()
    assert tl.all_thoughts() == []


def test_persists_to_file(tmp_path):
    import json
    p = str(tmp_path / "thoughts.jsonl")
    tl = ThoughtLogger(path=p)
    tl.log("agent", "thinking step")
    lines = (tmp_path / "thoughts.jsonl").read_text().splitlines()
    data = json.loads(lines[0])
    assert data["agent"] == "agent"
