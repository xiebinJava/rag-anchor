"""Tests for evaluation dataset loading and the evaluation runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from rag_anchor.evaluation.models import (
    SUPPORTED_DATASET_VERSIONS,
    load_evaluation_dataset,
)
from rag_anchor.evaluation.runner import run_evaluation
from rag_anchor.rag.query import QueryService
from rag_anchor.rag.source import MarkdownFixtureSource, default_fixture_source

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = REPO_ROOT / "evals" / "sets" / "rag-anchor-v1.yaml"
EVAL_ROOT = REPO_ROOT / "fixtures" / "evaluation"


def test_dataset_rejects_missing_case_id() -> None:
    payload = {
        "dataset_version": "rag-anchor-v1",
        "knowledge_root": "fixtures/evaluation",
        "embedding_mode": "lexical",
        "cases": [{"question": "hello", "expected_document_ids": ["chinese"]}],
    }
    with pytest.raises(ValidationError):
        load_evaluation_dataset(payload, repo_root=REPO_ROOT)


def test_dataset_rejects_empty_question() -> None:
    payload = {
        "dataset_version": "rag-anchor-v1",
        "knowledge_root": "fixtures/evaluation",
        "embedding_mode": "lexical",
        "cases": [
            {
                "case_id": "empty-q",
                "question": "   ",
                "expected_document_ids": ["chinese"],
            }
        ],
    }
    with pytest.raises(ValidationError):
        load_evaluation_dataset(payload, repo_root=REPO_ROOT)


def test_dataset_rejects_no_answer_with_expected_sources() -> None:
    payload = {
        "dataset_version": "rag-anchor-v1",
        "knowledge_root": "fixtures/evaluation",
        "embedding_mode": "lexical",
        "cases": [
            {
                "case_id": "conflict",
                "question": "missing topic",
                "expected_document_ids": ["chinese"],
                "is_no_answer": True,
            }
        ],
    }
    with pytest.raises(ValidationError):
        load_evaluation_dataset(payload, repo_root=REPO_ROOT)


def test_dataset_rejects_duplicate_case_ids() -> None:
    payload = {
        "dataset_version": "rag-anchor-v1",
        "knowledge_root": "fixtures/evaluation",
        "embedding_mode": "lexical",
        "cases": [
            {
                "case_id": "dup",
                "question": "one",
                "expected_document_ids": ["chinese"],
            },
            {
                "case_id": "dup",
                "question": "two",
                "expected_document_ids": ["english"],
            },
        ],
    }
    with pytest.raises(ValidationError):
        load_evaluation_dataset(payload, repo_root=REPO_ROOT)


def test_dataset_rejects_unsupported_version() -> None:
    payload: dict[str, Any] = {
        "dataset_version": "unsupported-v9",
        "knowledge_root": "fixtures/evaluation",
        "embedding_mode": "lexical",
        "cases": [
            {
                "case_id": "x",
                "question": "q",
                "expected_document_ids": [],
                "is_no_answer": True,
            }
        ],
    }
    with pytest.raises(ValidationError):
        load_evaluation_dataset(payload, repo_root=REPO_ROOT)


def test_loads_manifest_from_yaml_file() -> None:
    dataset = load_evaluation_dataset(DATASET_PATH, repo_root=REPO_ROOT)
    assert dataset.dataset_version in SUPPORTED_DATASET_VERSIONS
    assert dataset.knowledge_root == EVAL_ROOT
    assert dataset.embedding_mode == "lexical"
    assert len(dataset.cases) >= 12
    no_answer_cases = [case for case in dataset.cases if case.is_no_answer]
    assert len(no_answer_cases) >= 3


def test_run_evaluation_uses_dataset_knowledge_root_not_default_fixture() -> None:
    dataset = load_evaluation_dataset(DATASET_PATH, repo_root=REPO_ROOT)
    default_service = QueryService(default_fixture_source())
    eval_service = QueryService(MarkdownFixtureSource(dataset.knowledge_root))

    default_report = run_evaluation(
        DATASET_PATH,
        default_service,
        embedding_mode="lexical",
        repo_root=REPO_ROOT,
    )
    eval_report = run_evaluation(
        DATASET_PATH,
        eval_service,
        embedding_mode="lexical",
        repo_root=REPO_ROOT,
    )

    assert eval_report.metrics["retrieval_recall_at_3"] >= 0.8
    assert eval_report.metrics["citation_resolution_rate"] == 1.0
    assert eval_report.metrics["no_answer_precision"] == 1.0
    assert default_report.failed_case_ids != eval_report.failed_case_ids or (
        default_report.metrics["retrieval_recall_at_3"]
        < eval_report.metrics["retrieval_recall_at_3"]
    )


def test_run_evaluation_is_deterministic() -> None:
    service = QueryService(MarkdownFixtureSource(EVAL_ROOT))
    first = run_evaluation(
        DATASET_PATH,
        service,
        embedding_mode="lexical",
        repo_root=REPO_ROOT,
    )
    second = run_evaluation(
        DATASET_PATH,
        service,
        embedding_mode="lexical",
        repo_root=REPO_ROOT,
    )
    assert {
        key: value for key, value in first.metrics.items() if key != "latency_ms"
    } == {key: value for key, value in second.metrics.items() if key != "latency_ms"}
    assert first.failed_case_ids == second.failed_case_ids


def test_fixed_vector_mode_is_not_wired_yet() -> None:
    service = QueryService(MarkdownFixtureSource(EVAL_ROOT))
    with pytest.raises(RuntimeError, match="not wired yet"):
        run_evaluation(
            DATASET_PATH,
            service,
            embedding_mode="fixed_vector",
            repo_root=REPO_ROOT,
        )


def test_query_service_respects_top_k_for_citations() -> None:
    service = QueryService(MarkdownFixtureSource(EVAL_ROOT))
    result = service.query(
        "RAG_ANCHOR_CHUNK_SIZE RAG_ANCHOR_CHUNK_OVERLAP configuration keys",
        top_k=1,
    )
    assert len(result.evidence) == 1
