"""In-memory domain models for fixture-backed retrieval."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChunkRecord:
    chunk_id: str
    document_id: str
    revision_id: str
    title: str
    source_url: str
    text: str
    position: int
    score: float = 0.0


@dataclass(frozen=True, slots=True)
class DocumentRecord:
    document_id: str
    revision_id: str
    title: str
    source_url: str
    chunks: tuple[ChunkRecord, ...]
    metadata: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class CitationRecord:
    chunk_id: str
    document_id: str
    revision_id: str
    title: str
    source_url: str
    text: str
    position: int


@dataclass(frozen=True, slots=True)
class QueryResponse:
    answer: str | None
    citations: tuple[CitationRecord, ...]
    no_answer: bool
    retrieved_document_ids: tuple[str, ...]
    retriever_version: str
    latency_ms: float
