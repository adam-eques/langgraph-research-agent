from __future__ import annotations
from research_agent.query_intent import detect_intent, IntentType


def test_detect_summarize():
    qi = detect_intent("Please summarize the latest AI research")
    assert qi.intent == IntentType.SUMMARIZE


def test_detect_compare():
    qi = detect_intent("Compare LangChain vs LangGraph for agents")
    assert qi.intent == IntentType.COMPARE


def test_detect_explain():
    qi = detect_intent("What is retrieval augmented generation?")
    assert qi.intent == IntentType.EXPLAIN


def test_keywords_extracted():
    qi = detect_intent("Research the impact of large language models")
    assert len(qi.keywords) > 0


def test_unknown_intent():
    qi = detect_intent("hello there")
    assert qi.confidence == 0.0
