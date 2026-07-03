from __future__ import annotations

from research_agent.doc_summarizer import (
    extractive_summary,
    merge_summaries,
    summarize_batch,
    truncate_summary,
)


def test_extractive_summary_sentence_count():
    text = "AI is amazing. It uses neural networks. Deep learning is a subset. Transformers changed NLP."
    summary = extractive_summary(text, num_sentences=2)
    assert len(summary) > 0


def test_truncate_at_sentence_boundary():
    text = "First sentence ends here. Second sentence is longer. Third one."
    truncated = truncate_summary(text, max_chars=40)
    assert truncated.endswith(".")


def test_summarize_batch():
    docs = ["Doc one. It covers topic A. Very important.", "Doc two. It covers topic B."]
    summaries = summarize_batch(docs, num_sentences=1)
    assert len(summaries) == 2


def test_merge_summaries_deduplicates():
    merged = merge_summaries(["Summary A.", "Summary A.", "Summary B."])
    assert merged.count("Summary A.") == 1
