"""Unit tests for RAG evaluation metrics."""

from rag_anchor.evaluation.metrics import (
    citation_resolution_rate,
    grounded_answer_rate,
    no_answer_precision,
    retrieval_recall_at_k,
)


def test_retrieval_recall_at_k_counts_hits_in_top_k() -> None:
    cases = (
        (("doc-a",), ("doc-a", "doc-b", "doc-c"), False),
        (("doc-x",), ("doc-a", "doc-b", "doc-c"), False),
        (("doc-a", "doc-b"), ("doc-a", "other", "doc-b"), False),
    )
    assert retrieval_recall_at_k(cases, k=3) == 2 / 3


def test_citation_resolution_rate_requires_resolvable_citations() -> None:
    cases = (
        (True, True),
        (True, False),
        (False, True),
    )
    assert citation_resolution_rate(cases) == 2 / 3


def test_grounded_answer_rate_counts_answered_cases_with_grounding() -> None:
    cases = (
        (False, True, True),
        (False, False, True),
        (True, False, True),
    )
    assert grounded_answer_rate(cases) == 1 / 2


def test_no_answer_precision_counts_correct_rejections() -> None:
    cases = (
        (True, True),
        (True, False),
        (False, True),
    )
    assert no_answer_precision(cases) == 1 / 2
