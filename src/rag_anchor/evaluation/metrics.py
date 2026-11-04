"""Evaluation metric helpers."""

from __future__ import annotations


def retrieval_recall_at_k(
    cases: tuple[tuple[tuple[str, ...], tuple[str, ...], bool], ...],
    *,
    k: int,
) -> float:
    if not cases:
        return 1.0
    hits = 0
    answer_cases = [case for case in cases if not case[2]]
    for expected_documents, retrieved_documents, is_no_answer in cases:
        if is_no_answer:
            continue
        top_documents = retrieved_documents[:k]
        if all(document_id in top_documents for document_id in expected_documents):
            hits += 1
    if not answer_cases:
        return 1.0
    return hits / len(answer_cases)


def citation_resolution_rate(cases: tuple[tuple[bool, bool], ...]) -> float:
    if not cases:
        return 1.0
    resolved = sum(1 for _expected, ok in cases if ok)
    return resolved / len(cases)


def grounded_answer_rate(
    cases: tuple[tuple[bool, bool, bool], ...],
) -> float:
    answer_cases = [case for case in cases if not case[0]]
    if not answer_cases:
        return 1.0
    grounded = sum(
        1
        for _no_answer, has_answer, is_grounded in answer_cases
        if is_grounded and has_answer
    )
    return grounded / len(answer_cases)


def no_answer_precision(cases: tuple[tuple[bool, bool], ...]) -> float:
    no_answer_cases = [case for case in cases if case[0]]
    if not no_answer_cases:
        return 1.0
    correct = sum(1 for _is_no_answer, is_correct in no_answer_cases if is_correct)
    return correct / len(no_answer_cases)
