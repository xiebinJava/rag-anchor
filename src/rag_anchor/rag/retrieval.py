"""Deterministic lexical retrieval for fixture-backed documents."""

from __future__ import annotations

import re

from rag_anchor.rag.models import ChunkRecord, DocumentRecord

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]+")
RETRIEVER_VERSION = "lexical-v1"


def _tokenize(text: str) -> tuple[str, ...]:
    raw_tokens = _TOKEN_PATTERN.findall(text.lower())
    tokens: list[str] = []
    for token in raw_tokens:
        if len(token) <= 1:
            continue
        tokens.append(token)
        if re.fullmatch(r"[\u4e00-\u9fff]+", token) and len(token) > 2:
            for index in range(len(token) - 1):
                bigram = token[index : index + 2]
                tokens.append(bigram)
    return tuple(tokens)


def _score_chunk(question_tokens: tuple[str, ...], chunk: ChunkRecord) -> float:
    if not question_tokens:
        return 0.0
    chunk_text = chunk.text.lower()
    score = 0.0
    for token in question_tokens:
        if token in chunk_text:
            score += 1.0
        if "_" in token:
            for part in token.split("_"):
                if len(part) > 1 and part in chunk_text:
                    score += 0.5
    return score


class LexicalRetriever:
    """Rank chunks by simple token overlap."""

    def retrieve(
        self,
        *,
        question: str,
        documents: tuple[DocumentRecord, ...],
        top_k: int,
    ) -> tuple[ChunkRecord, ...]:
        question_tokens = _tokenize(question)
        ranked: list[ChunkRecord] = []
        for document in documents:
            for chunk in document.chunks:
                score = _score_chunk(question_tokens, chunk)
                if score <= 0:
                    continue
                ranked.append(
                    ChunkRecord(
                        chunk_id=chunk.chunk_id,
                        document_id=chunk.document_id,
                        revision_id=chunk.revision_id,
                        title=chunk.title,
                        source_url=chunk.source_url,
                        text=chunk.text,
                        position=chunk.position,
                        score=score,
                    )
                )
        ranked.sort(
            key=lambda item: (
                -item.score,
                item.document_id,
                item.position,
                item.chunk_id,
            )
        )
        return tuple(ranked[:top_k])
