"""Query orchestration over fixture-backed lexical retrieval."""

from __future__ import annotations

import time

from rag_anchor.rag.models import CitationRecord, QueryResponse
from rag_anchor.rag.retrieval import RETRIEVER_VERSION, LexicalRetriever
from rag_anchor.rag.source import MarkdownFixtureSource


class QueryService:
    """Run deterministic retrieval and evidence-style answers for fixtures."""

    def __init__(
        self,
        *,
        source: MarkdownFixtureSource,
        retriever: LexicalRetriever | None = None,
    ) -> None:
        self._source = source
        self._retriever = retriever or LexicalRetriever()
        self._documents = source.load_documents()
        self._chunk_index = source.chunk_index()

    def query(self, question: str, *, top_k: int = 3) -> QueryResponse:
        started = time.perf_counter()
        retrieved = self._retriever.retrieve(
            question=question,
            documents=self._documents,
            top_k=top_k,
        )
        if not retrieved:
            latency_ms = (time.perf_counter() - started) * 1000
            return QueryResponse(
                answer=None,
                citations=(),
                no_answer=True,
                retrieved_document_ids=(),
                retriever_version=RETRIEVER_VERSION,
                latency_ms=latency_ms,
            )

        citations = tuple(
            CitationRecord(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                revision_id=chunk.revision_id,
                title=chunk.title,
                source_url=chunk.source_url,
                text=chunk.text,
                position=chunk.position,
            )
            for chunk in retrieved
        )
        answer = "\n\n".join(citation.text for citation in citations)
        latency_ms = (time.perf_counter() - started) * 1000
        document_ids = tuple(dict.fromkeys(chunk.document_id for chunk in retrieved))
        return QueryResponse(
            answer=answer,
            citations=citations,
            no_answer=False,
            retrieved_document_ids=document_ids,
            retriever_version=RETRIEVER_VERSION,
            latency_ms=latency_ms,
        )

    def resolve_citation(self, chunk_id: str) -> CitationRecord | None:
        chunk = self._chunk_index.get(chunk_id)
        if chunk is None:
            return None
        return CitationRecord(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            revision_id=chunk.revision_id,
            title=chunk.title,
            source_url=chunk.source_url,
            text=chunk.text,
            position=chunk.position,
        )
