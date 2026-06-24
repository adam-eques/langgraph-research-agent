from __future__ import annotations
from research_agent.agents.key_terms_extractor import (
    KeyTerm,
    extract_single_terms,
    extract_named_phrases,
    extract_key_terms,
)


def test_extract_single_terms():
    text = "machine learning deep learning neural networks training"
    terms = extract_single_terms(text)
    term_names = [t.term for t in terms]
    assert "learning" in term_names or "machine" in term_names


def test_extract_single_terms_stopwords_excluded():
    text = "the and or a this that is are"
    terms = extract_single_terms(text)
    assert all(t.term not in {"the", "and", "this"} for t in terms)


def test_extract_named_phrases():
    text = "Natural Language Processing and Machine Learning are growing fields."
    phrases = extract_named_phrases(text)
    names = [p.term for p in phrases]
    assert any("Natural Language" in n for n in names) or any("Machine Learning" in n for n in names)


def test_extract_key_terms_top_n():
    text = "deep learning is a subset of machine learning which is a subset of artificial intelligence"
    terms = extract_key_terms(text, top_n=5)
    assert len(terms) <= 5


def test_extract_key_terms_no_duplicates():
    text = "python python python is the best language for machine learning"
    terms = extract_key_terms(text)
    term_names = [t.term for t in terms]
    assert len(term_names) == len(set(term_names))


def test_key_term_to_dict():
    kt = KeyTerm("neural", 5, 0.8)
    d = kt.to_dict()
    assert d["frequency"] == 5 and d["is_phrase"] is False
