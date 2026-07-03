"""Evaluation metric functions for the research pipeline."""

from __future__ import annotations

import logging
import re
from collections import Counter

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pure-Python token-based metrics (no LLM required)
# ---------------------------------------------------------------------------


def _tokenise(text: str) -> list[str]:
    """Lowercase and split *text* into word tokens."""
    return re.findall(r"\b\w+\b", text.lower())


def f1_score(prediction: str, ground_truth: str) -> float:
    """Compute token-level F1 score between *prediction* and *ground_truth*.

    This is the standard SQuAD-style exact-match / F1 metric applied at the
    token level.  Tokens are lowercased; punctuation is ignored.

    Parameters
    ----------
    prediction:
        The model's answer string.
    ground_truth:
        The expected / reference answer string.

    Returns
    -------
    float
        F1 score in the range [0, 1].
    """
    pred_tokens = Counter(_tokenise(prediction))
    gt_tokens = Counter(_tokenise(ground_truth))

    common = sum((pred_tokens & gt_tokens).values())
    if common == 0:
        return 0.0

    precision = common / sum(pred_tokens.values())
    recall = common / sum(gt_tokens.values())
    return 2 * precision * recall / (precision + recall)


def context_recall(expected: str, retrieved: list[str]) -> float:
    """Measure how much of the expected content is covered by retrieved passages.

    Uses token-level overlap as a proxy for recall.  A retrieved passage
    "covers" a token from *expected* if that token appears in any retrieved
    passage.

    Parameters
    ----------
    expected:
        The reference answer or expected content.
    retrieved:
        List of retrieved passage strings.

    Returns
    -------
    float
        Recall score in the range [0, 1].  Returns 0 if *retrieved* is empty.
    """
    if not retrieved:
        return 0.0

    expected_tokens = set(_tokenise(expected))
    if not expected_tokens:
        return 1.0  # vacuously true

    combined_retrieved = " ".join(retrieved)
    retrieved_tokens = set(_tokenise(combined_retrieved))

    covered = expected_tokens & retrieved_tokens
    return len(covered) / len(expected_tokens)


# ---------------------------------------------------------------------------
# LLM-based metrics (require an Anthropic API key)
# ---------------------------------------------------------------------------


def answer_relevance(query: str, answer: str) -> float:
    """Score how relevant *answer* is to *query* using an LLM judge (0-1).

    The LLM is asked to rate relevance on a 0-10 integer scale; the score is
    normalised to [0, 1].  If the LLM call fails, falls back to a simple
    keyword overlap heuristic.

    Parameters
    ----------
    query:
        The original research question.
    answer:
        The generated answer to evaluate.

    Returns
    -------
    float
        Relevance score in [0, 1].
    """
    try:
        return _llm_score(
            prompt=(
                "You are an evaluation judge. Rate how relevant the following ANSWER is to the "
                "QUESTION on a scale of 0 to 10 where 10 means perfectly relevant and 0 means "
                "completely irrelevant.\n\n"
                f"QUESTION: {query}\n\n"
                f"ANSWER: {answer}\n\n"
                "Respond with ONLY a single integer from 0 to 10."
            )
        )
    except Exception:
        logger.warning("answer_relevance LLM call failed — using keyword fallback")
        return _keyword_overlap(query, answer)


def faithfulness(answer: str, context: str) -> float:
    """Score whether *answer* is grounded in *context* using an LLM judge (0-1).

    A faithfulness score of 1 means every claim in the answer can be traced
    back to the context.  A score of 0 means the answer hallucinated everything.

    Parameters
    ----------
    answer:
        The generated answer to evaluate.
    context:
        The retrieved context passages the answer should be based on.

    Returns
    -------
    float
        Faithfulness score in [0, 1].
    """
    try:
        return _llm_score(
            prompt=(
                "You are a faithfulness evaluator. Given a CONTEXT and an ANSWER, rate how "
                "faithful the answer is to the context on a scale of 0 to 10. "
                "10 means every claim in the answer is supported by the context. "
                "0 means the answer contradicts or fabricates information not in the context.\n\n"
                f"CONTEXT:\n{context[:3000]}\n\n"
                f"ANSWER:\n{answer}\n\n"
                "Respond with ONLY a single integer from 0 to 10."
            )
        )
    except Exception:
        logger.warning("faithfulness LLM call failed — using keyword fallback")
        return _keyword_overlap(context, answer)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _llm_score(prompt: str) -> float:
    """Call the LLM with *prompt* and parse a 0-10 integer from the response."""
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage

    from research_agent.config import config

    llm = ChatAnthropic(
        model=config.default_model,
        temperature=0,
        max_tokens=8,
        api_key=config.anthropic_api_key,
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    raw = str(response.content).strip()

    # Extract first integer 0-10
    match = re.search(r"\b([0-9]|10)\b", raw)
    if match:
        return int(match.group(1)) / 10.0
    logger.warning("Could not parse LLM score from: %r", raw)
    return 0.5  # neutral fallback


def _keyword_overlap(source: str, target: str) -> float:
    """Simple keyword overlap as a fallback metric."""
    source_tokens = set(_tokenise(source))
    target_tokens = set(_tokenise(target))
    if not source_tokens:
        return 0.0
    overlap = source_tokens & target_tokens
    return len(overlap) / len(source_tokens)
