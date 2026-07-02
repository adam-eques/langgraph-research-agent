from __future__ import annotations

from research_agent.agents.metadata_enricher import (
    enrich_batch,
    enrich_document,
    extract_doi,
    extract_year,
    infer_content_type,
)


def test_extract_year():
    assert extract_year("Published in 2023 by the journal.") == 2023


def test_extract_year_none():
    assert extract_year("No year found here.") is None


def test_extract_doi():
    text = "See https://doi.org/ 10.1145/1234567.890 for details."
    doi = extract_doi(text)
    assert doi is not None and doi.startswith("10.")


def test_infer_content_type_academic():
    text = "Abstract. DOI: 10.1000/xyz. This paper studies..."
    assert infer_content_type(text) == "academic_paper"


def test_enrich_document():
    text = "This paper was published in 2021. DOI: 10.9999/abc.def"
    doc = enrich_document("d1", text, url="https://arxiv.org/abs/123")
    assert doc.enriched_metadata["year"] == 2021
    assert "arxiv.org" in doc.enriched_metadata.get("domain", "")
    assert doc.enriched_metadata["word_count"] > 0


def test_enrich_batch():
    docs = [
        {"id": "a", "text": "Research from 2022.", "metadata": {}},
        {"id": "b", "text": "Another document without year.", "metadata": {}},
    ]
    results = enrich_batch(docs)
    assert len(results) == 2
    assert results[0].enriched_metadata.get("year") == 2022
