"""Execute evaluation datasets against a query service."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Literal

from rag_anchor.evaluation.metrics import (
    citation_resolution_rate,
    grounded_answer_rate,
    no_answer_precision,
    retrieval_recall_at_k,
)
from rag_anchor.evaluation.models import EvaluationReport, load_evaluation_dataset
from rag_anchor.rag.models import Chunk
from rag_anchor.rag.query import QueryService
from rag_anchor.rag.retrieval import chunk_documents
from rag_anchor.rag.source import MarkdownFixtureSource

RECALL_AT_K = 3
RETRIEVER_VERSION = "lexical-v1"


class EvaluationRunner:
    """Run a versioned dataset and compute quality metrics."""

    def run(
        self,
        dataset_path: Path,
        service: QueryService,
        embedding_mode: Literal["lexical", "fixed_vector"] | None = None,
        *,
        repo_root: Path | None = None,
    ) -> EvaluationReport:
        return run_evaluation(
            dataset_path,
            service,
            embedding_mode=embedding_mode,
            repo_root=repo_root,
        )


def _chunk_index_for_root(knowledge_root: Path) -> dict[str, Chunk]:
    source = MarkdownFixtureSource(knowledge_root)
    return {chunk.chunk_id: chunk for chunk in chunk_documents(source.load_documents())}


def run_evaluation(
    dataset_path: Path,
    service: QueryService,
    embedding_mode: Literal["lexical", "fixed_vector"] | None = None,
    *,
    repo_root: Path | None = None,
) -> EvaluationReport:
    root = repo_root or Path(__file__).resolve().parents[3]
    dataset = load_evaluation_dataset(dataset_path, repo_root=root)
    mode = embedding_mode or dataset.embedding_mode
    if mode == "fixed_vector":
        msg = "embedding_mode fixed_vector is not wired yet; use lexical for Task 1"
        raise RuntimeError(msg)
    if mode != "lexical":
        msg = f"unsupported embedding_mode: {mode}"
        raise ValueError(msg)

    chunk_index = _chunk_index_for_root(dataset.knowledge_root)
    failed_case_ids: list[str] = []
    recall_inputs: list[tuple[tuple[str, ...], tuple[str, ...], bool]] = []
    citation_inputs: list[tuple[bool, bool]] = []
    grounded_inputs: list[tuple[bool, bool, bool]] = []
    no_answer_inputs: list[tuple[bool, bool]] = []
    latencies: list[float] = []

    for case in dataset.cases:
        started = time.perf_counter()
        result = service.query(case.question, case.top_k)
        latencies.append((time.perf_counter() - started) * 1000)

        retrieved_documents = tuple(
            dict.fromkeys(item.chunk.document_id for item in result.evidence)
        )
        recall_inputs.append(
            (case.expected_document_ids, retrieved_documents, case.is_no_answer)
        )

        citations_resolved = all(
            item.chunk.chunk_id in chunk_index for item in result.evidence
        )
        citation_inputs.append((not case.is_no_answer, citations_resolved))

        has_answer = result.answer is not None and result.answer.strip() != ""
        grounded = (
            citations_resolved
            and has_answer
            and bool(result.evidence)
            and not result.no_answer
        )
        grounded_inputs.append((case.is_no_answer, has_answer, grounded))

        no_answer_correct = result.no_answer and not has_answer
        no_answer_inputs.append((case.is_no_answer, no_answer_correct))

        case_passed = True
        if case.is_no_answer:
            if not no_answer_correct:
                case_passed = False
        else:
            top_documents = retrieved_documents[:RECALL_AT_K]
            if not all(
                doc_id in top_documents for doc_id in case.expected_document_ids
            ):
                case_passed = False
            if not grounded:
                case_passed = False

        if not case_passed:
            failed_case_ids.append(case.case_id)

    metrics = {
        f"retrieval_recall_at_{RECALL_AT_K}": retrieval_recall_at_k(
            tuple(recall_inputs),
            k=RECALL_AT_K,
        ),
        "citation_resolution_rate": citation_resolution_rate(tuple(citation_inputs)),
        "grounded_answer_rate": grounded_answer_rate(tuple(grounded_inputs)),
        "no_answer_precision": no_answer_precision(tuple(no_answer_inputs)),
        "latency_ms": sum(latencies) / len(latencies) if latencies else 0.0,
    }

    return EvaluationReport(
        dataset_version=dataset.dataset_version,
        retriever_version=RETRIEVER_VERSION,
        embedding_version=None,
        metrics=metrics,
        failed_case_ids=tuple(failed_case_ids),
    )
