"""Execute evaluation datasets against a query service."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from rag_anchor.evaluation.metrics import (
    citation_resolution_rate,
    grounded_answer_rate,
    no_answer_precision,
    retrieval_recall_at_k,
)
from rag_anchor.evaluation.models import (
    EvaluationReport,
    load_evaluation_dataset,
)
from rag_anchor.rag.query import QueryService

RECALL_AT_K = 3


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

    failed_case_ids: list[str] = []
    recall_inputs: list[tuple[tuple[str, ...], tuple[str, ...], bool]] = []
    citation_inputs: list[tuple[bool, bool]] = []
    grounded_inputs: list[tuple[bool, bool, bool]] = []
    no_answer_inputs: list[tuple[bool, bool]] = []
    latencies: list[float] = []
    retriever_version = ""

    for case in dataset.cases:
        response = service.query(case.question, top_k=case.top_k)
        if not retriever_version:
            retriever_version = response.retriever_version

        latencies.append(response.latency_ms)
        retrieved_documents = response.retrieved_document_ids
        recall_inputs.append(
            (case.expected_document_ids, retrieved_documents, case.is_no_answer)
        )

        citations_resolved = all(
            service.resolve_citation(citation.chunk_id) is not None
            for citation in response.citations
        )
        citation_inputs.append((not case.is_no_answer, citations_resolved))

        has_answer = response.answer is not None and response.answer.strip() != ""
        grounded = citations_resolved and has_answer and bool(response.citations)
        grounded_inputs.append((case.is_no_answer, has_answer, grounded))

        no_answer_correct = response.no_answer and not has_answer
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
            if not citations_resolved or not has_answer or not response.citations:
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
        retriever_version=retriever_version or "unknown",
        embedding_version=None,
        metrics=metrics,
        failed_case_ids=tuple(failed_case_ids),
    )
