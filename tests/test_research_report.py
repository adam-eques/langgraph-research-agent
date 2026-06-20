from __future__ import annotations

import json
from research_agent.research_report import ResearchReport


def test_to_dict_keys():
    report = ResearchReport(query="q", answer="a", confidence=0.9)
    d = report.to_dict()
    assert "query" in d and "answer" in d and "confidence" in d


def test_to_json():
    report = ResearchReport(query="q", answer="a")
    data = json.loads(report.to_json())
    assert data["query"] == "q"


def test_from_dict_roundtrip():
    original = ResearchReport(query="test", answer="result", confidence=0.85, model="claude")
    restored = ResearchReport.from_dict(original.to_dict())
    assert restored.query == "test"
    assert restored.confidence == 0.85


def test_default_version():
    report = ResearchReport(query="q", answer="a")
    assert report.version == "1.0"
