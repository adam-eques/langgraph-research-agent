from __future__ import annotations

import time

from research_agent.benchmark_runner import BenchmarkResult, BenchmarkRunner


def test_run_basic():
    runner = BenchmarkRunner()
    result = runner.run("noop", lambda: None, iterations=5)
    assert isinstance(result, BenchmarkResult)
    assert result.iterations == 5 and result.mean_ms >= 0


def test_run_registers_result():
    runner = BenchmarkRunner()
    runner.run("fn1", lambda: None, iterations=3)
    assert len(runner.summary()) == 1


def test_compare():
    runner = BenchmarkRunner()
    runner.run("fast", lambda: None, iterations=10)
    runner.run("slow", lambda: time.sleep(0.001), iterations=10)
    ratios = runner.compare("fast")
    assert "slow" in ratios and ratios["slow"] >= 1.0


def test_fastest():
    runner = BenchmarkRunner()
    runner.run("a", lambda: None, iterations=5)
    runner.run("b", lambda: time.sleep(0.005), iterations=5)
    fastest = runner.fastest()
    assert fastest.name == "a"


def test_to_dict():
    r = BenchmarkResult("test", 100.0, 10, 10.0, 5.0, 20.0)
    d = r.to_dict()
    assert "mean_ms" in d and d["iterations"] == 10


def test_no_results_fastest():
    runner = BenchmarkRunner()
    assert runner.fastest() is None
