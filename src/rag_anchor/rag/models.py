"""Domain models for the deterministic query path."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Document:
    """A source document that can be split into retrievable chunks."""

    document_id: str
    title: str
    source_url: str
    content: str


@dataclass(frozen=True, slots=True)
class Chunk:
    """A source paragraph with stable citation metadata."""

    chunk_id: str
    document_id: str
    title: str
    source_url: str
    text: str
    position: int


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """A chunk ranked by the local deterministic retriever."""

    chunk: Chunk
    score: int


@dataclass(frozen=True, slots=True)
class QueryResult:
    """The internal result used to build the public query response."""

    answer: str | None
    evidence: tuple[RetrievedChunk, ...]
    no_answer: bool
