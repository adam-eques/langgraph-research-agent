from __future__ import annotations
from research_agent.perf_logger import PerfLogger


def test_log_and_stats(tmp_path):
    pl = PerfLogger(str(tmp_path / "perf.jsonl"))
    pl.log("retrieve", 120.5, tokens_in=200, tokens_out=50)
    pl.log("synthesize", 80.3, tokens_in=500, tokens_out=300)
    stats = pl.session_stats()
    assert stats["count"] == 2 and stats["total_tokens"] == 1050


def test_log_writes_to_file(tmp_path):
    path = tmp_path / "perf.jsonl"
    pl = PerfLogger(str(path))
    pl.log("op", 10.0)
    lines = path.read_text().splitlines()
    assert len(lines) == 1 and "op" in lines[0]


def test_empty_stats():
    pl = PerfLogger("/dev/null")
    assert pl.session_stats() == {}
