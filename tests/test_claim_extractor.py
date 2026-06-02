from __future__ import annotations
from research_agent.agents.claim_extractor import extract_claims, filter_claims_by_type


def test_extract_assertion_claims():
    text = "Python is a popular language. AI is transforming industries."
    claims = extract_claims(text)
    assert any(c.claim_type == "assertion" for c in claims)


def test_extract_evidence_claims():
    text = "Studies show that RAG improves accuracy significantly in most benchmarks."
    claims = extract_claims(text)
    assert any(c.claim_type == "evidence" for c in claims)


def test_filter_by_type():
    text = "AI is growing. Studies show neural networks are effective."
    claims = extract_claims(text)
    assertions = filter_claims_by_type(claims, "assertion")
    assert all(c.claim_type == "assertion" for c in assertions)


def test_confidence_range():
    text = "Machine learning is revolutionizing medicine according to experts."
    claims = extract_claims(text, min_confidence=0.3)
    assert all(0.0 <= c.confidence <= 1.0 for c in claims)
