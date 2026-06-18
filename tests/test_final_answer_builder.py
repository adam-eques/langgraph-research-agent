from __future__ import annotations
from research_agent.final_answer_builder import build_final_answer, FinalAnswer


def test_build_with_model_answer():
    answer = build_final_answer("What is AI?", [], [], model_answer="AI is intelligence.")
    assert answer.answer == "AI is intelligence."


def test_build_from_notes():
    notes = ["AI drives automation.", "ML is a subset."]
    answer = build_final_answer("Q?", notes, [])
    assert "AI" in answer.answer or "ML" in answer.answer


def test_citations_deduplicated():
    citations = [{"source": "s1"}, {"source": "s1"}, {"source": "s2"}]
    answer = build_final_answer("Q?", [], citations, model_answer="ans")
    assert len(answer.citations) == 2


def test_to_dict():
    fa = FinalAnswer("Q", "answer", [], 0.9, {})
    d = fa.to_dict()
    assert "has_citations" in d and "confidence" in d


def test_format_with_citations():
    fa = FinalAnswer("Q", "My answer.", [{"source": "src1", "excerpt": "relevant"}])
    formatted = fa.format_with_citations()
    assert "References:" in formatted and "src1" in formatted
