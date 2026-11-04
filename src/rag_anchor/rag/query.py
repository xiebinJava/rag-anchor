"""Query orchestration behind the HTTP interface."""

from dataclasses import dataclass
from typing import Protocol

from rag_anchor.rag.models import QueryResult, RetrievedChunk
from rag_anchor.rag.retrieval import LexicalRetriever, Retriever, chunk_documents
from rag_anchor.rag.source import KnowledgeSource


class AnswerGenerator(Protocol):
    """Generate an answer using only the retrieved evidence."""

    def generate(self, question: str, evidence: tuple[RetrievedChunk, ...]) -> str: ...


@dataclass(frozen=True, slots=True)
class DeterministicAnswerGenerator:
    """Return the highest-ranked evidence without adding unsupported text."""

    def generate(self, question: str, evidence: tuple[RetrievedChunk, ...]) -> str:
        del question
        return evidence[0].chunk.text


class QueryService:
    """Coordinate a source, retriever, and evidence-grounded answerer."""

    def __init__(
        self,
        source: KnowledgeSource,
        retriever: Retriever | None = None,
        answer_generator: AnswerGenerator | None = None,
    ) -> None:
        chunks = chunk_documents(source.load_documents())
        self._retriever = retriever or LexicalRetriever(chunks)
        self._answer_generator = answer_generator or DeterministicAnswerGenerator()

    def query(self, question: str, top_k: int) -> QueryResult:
        evidence = self._retriever.retrieve(question, top_k)
        if not evidence:
            return QueryResult(answer=None, evidence=(), no_answer=True)
        answer = self._answer_generator.generate(question, evidence)
        return QueryResult(answer=answer, evidence=evidence, no_answer=False)
