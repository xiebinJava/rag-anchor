"""Evaluation dataset models and YAML loading."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal, cast

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

SUPPORTED_DATASET_VERSIONS = frozenset({"rag-anchor-v1"})


class EvaluationCase(BaseModel):
    case_id: str
    question: str
    expected_document_ids: tuple[str, ...]
    expected_chunk_ids: tuple[str, ...] = ()
    is_no_answer: bool = False
    expected_citation_chunk_ids: tuple[str, ...] = ()
    top_k: int = Field(default=3, ge=1, le=5)

    @field_validator("case_id")
    @classmethod
    def validate_case_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            msg = "case_id must not be empty"
            raise ValueError(msg)
        return cleaned

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            msg = "question must not be empty"
            raise ValueError(msg)
        return cleaned


class EvaluationDataset(BaseModel):
    dataset_version: str
    knowledge_root: Path
    embedding_mode: Literal["lexical", "fixed_vector"]
    cases: tuple[EvaluationCase, ...]

    @field_validator("dataset_version")
    @classmethod
    def validate_dataset_version(cls, value: str) -> str:
        if value not in SUPPORTED_DATASET_VERSIONS:
            msg = f"unsupported dataset_version: {value}"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_cases(self) -> EvaluationDataset:
        seen: set[str] = set()
        for case in self.cases:
            if case.case_id in seen:
                msg = f"duplicate case_id: {case.case_id}"
                raise ValueError(msg)
            seen.add(case.case_id)
            if case.is_no_answer and case.expected_document_ids:
                msg = (
                    f"case {case.case_id} cannot set expected_document_ids "
                    "when is_no_answer is true"
                )
                raise ValueError(msg)
            if case.is_no_answer and case.expected_citation_chunk_ids:
                msg = (
                    f"case {case.case_id} cannot set expected_citation_chunk_ids "
                    "when is_no_answer is true"
                )
                raise ValueError(msg)
            if not case.is_no_answer and not case.expected_document_ids:
                msg = f"case {case.case_id} must declare expected_document_ids"
                raise ValueError(msg)
        return self


class EvaluationReport(BaseModel):
    dataset_version: str
    retriever_version: str
    embedding_version: str | None
    metrics: dict[str, float]
    failed_case_ids: tuple[str, ...]


def _coerce_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        msg = "evaluation dataset must be a mapping"
        raise TypeError(msg)
    return cast(dict[str, Any], payload)


def load_evaluation_dataset(
    dataset: Path | dict[str, Any],
    *,
    repo_root: Path,
) -> EvaluationDataset:
    if isinstance(dataset, Path):
        raw = yaml.safe_load(dataset.read_text(encoding="utf-8"))
    else:
        raw = dataset
    payload = _coerce_payload(raw)
    knowledge_root = Path(str(payload["knowledge_root"]))
    if not knowledge_root.is_absolute():
        knowledge_root = repo_root / knowledge_root
    payload["knowledge_root"] = knowledge_root
    cases = payload.get("cases", [])
    payload["cases"] = [
        {
            **case,
            "expected_document_ids": tuple(case.get("expected_document_ids", ())),
            "expected_chunk_ids": tuple(case.get("expected_chunk_ids", ())),
            "expected_citation_chunk_ids": tuple(
                case.get("expected_citation_chunk_ids", ())
            ),
        }
        for case in cases
    ]
    return EvaluationDataset.model_validate(payload)
