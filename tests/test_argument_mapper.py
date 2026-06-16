from __future__ import annotations
from research_agent.agents.argument_mapper import extract_argument_structure, ArgumentMap, Argument


def test_extracts_pro_arguments():
    text = "Studies show that LLMs improve productivity. Evidence supports widespread adoption."
    arg_map = extract_argument_structure(text, "LLMs")
    assert len(arg_map.arguments) >= 1


def test_extracts_counter_arguments():
    text = "However, LLMs have limitations in accuracy. Critics argue about hallucination."
    arg_map = extract_argument_structure(text, "LLMs")
    assert len(arg_map.counter_arguments) >= 1


def test_balance_score_range():
    am = ArgumentMap("AI")
    am.add_argument(Argument("pro1", "supports AI"))
    am.add_counter(Argument("con1", "challenges AI"))
    assert am.balance_score() == 0.5


def test_empty_text():
    arg_map = extract_argument_structure("", "nothing")
    assert arg_map.balance_score() == 0.5
