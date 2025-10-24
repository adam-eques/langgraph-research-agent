from __future__ import annotations

from research_agent.note_merger import merge_notes, extract_key_sentences, summarize_research_notes


def test_merge_deduplicates():
    notes = ["AI is powerful", "AI is powerful", "ML is great"]
    result = merge_notes(notes)
    assert result.count("AI is powerful") == 1


def test_merge_preserves_order():
    notes = ["First note here.", "Second note here."]
    result = merge_notes(notes, dedup=False)
    assert result.index("First") < result.index("Second")


def test_extract_key_sentences():
    text = "Short. This is a longer sentence with many words in it. Another long sentence here with details."
    sentences = extract_key_sentences(text, n=2)
    assert len(sentences) <= 2
    for s in sentences:
        assert len(s.split()) >= 8


def test_summarize_notes_returns_string():
    result = summarize_research_notes(["AI is evolving rapidly in many fields and applications."])
    assert isinstance(result, str)
