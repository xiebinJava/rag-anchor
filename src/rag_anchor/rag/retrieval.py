"""Deterministic chunking and lexical retrieval for local fixtures."""

import re
from dataclasses import dataclass
from typing import Protocol

from rag_anchor.rag.models import Chunk, Document, RetrievedChunk

TOKEN_PATTERN = re.compile(r"[a-z0-9_]+|[\u4e00-\u9fff]")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "does",
    "for",
    "from",
    "how",
    "is",
    "of",
    "the",
    "to",
    "what",
    "which",
    "with",
}


class Retriever(Protocol):
    """Return ranked evidence chunks for a question."""

    def retrieve(self, question: str, top_k: int) -> tuple[RetrievedChunk, ...]: ...


def chunk_documents(documents: tuple[Document, ...]) -> tuple[Chunk, ...]:
    """Split each document into stable paragraph-sized chunks."""

    chunks: list[Chunk] = []
    for document in documents:
        paragraphs = (
            paragraph.strip() for paragraph in re.split(r"\n\s*\n", document.content)
        )
        position = 0
        for paragraph in paragraphs:
            body = "\n".join(
                line for line in paragraph.splitlines() if not line.startswith("# ")
            ).strip()
            if not body:
                continue
            position += 1
            chunks.append(
                Chunk(
                    chunk_id=f"{document.document_id}-chunk-{position}",
                    document_id=document.document_id,
                    title=document.title,
                    source_url=document.source_url,
                    text=body,
                    position=position,
                )
            )
    return tuple(chunks)


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in TOKEN_PATTERN.findall(value.lower())
        if token not in STOP_WORDS
    }


@dataclass(frozen=True, slots=True)
class LexicalRetriever:
    """Rank chunks by the number of distinct query terms they contain."""

    chunks: tuple[Chunk, ...]

    def retrieve(self, question: str, top_k: int) -> tuple[RetrievedChunk, ...]:
        query_terms = _tokens(question)
        ranked = [
            RetrievedChunk(chunk=chunk, score=len(query_terms & _tokens(chunk.text)))
            for chunk in self.chunks
        ]
        matching = (item for item in ranked if item.score > 0)
        return tuple(
            sorted(
                matching,
                key=lambda item: (
                    -item.score,
                    item.chunk.position,
                    item.chunk.chunk_id,
                ),
            )[:top_k]
        )
