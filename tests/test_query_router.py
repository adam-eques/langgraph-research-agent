from __future__ import annotations

from research_agent.rag.query_router import RetrievalStrategy, route_query


def test_direct_factual_query():
    decision = route_query("Who is Alan Turing?")
    assert decision.strategy == RetrievalStrategy.DIRECT


def test_definition_query():
    decision = route_query("What is the definition of machine learning?")
    assert decision.strategy == RetrievalStrategy.DIRECT


def test_multi_hop_query():
    decision = route_query("How did the invention of transformers lead to the LLM revolution?")
    assert decision.strategy == RetrievalStrategy.MULTI_HOP


def test_keyword_search_query():
    decision = route_query('Search for "gradient descent" papers')
    assert decision.strategy == RetrievalStrategy.KEYWORD


def test_hybrid_default():
    decision = route_query("Explain recent advances in reinforcement learning")
    assert decision.strategy == RetrievalStrategy.HYBRID


def test_decision_to_dict():
    decision = route_query("What is AI?")
    d = decision.to_dict()
    assert "strategy" in d and "confidence" in d and "suggested_top_k" in d
