from __future__ import annotations

from research_agent.query_classifier import QueryType, classify_query


def test_factual_query():
    assert classify_query("What is machine learning?") == QueryType.FACTUAL


def test_analytical_query():
    assert classify_query("Why does RAG improve accuracy?") == QueryType.ANALYTICAL


def test_comparative_query():
    assert classify_query("Compare GPT-4 vs Claude") == QueryType.COMPARATIVE


def test_procedural_query():
    assert classify_query("How to set up LangGraph?") == QueryType.PROCEDURAL


def test_opinion_query():
    assert classify_query("Should I use LangChain?") == QueryType.OPINION
