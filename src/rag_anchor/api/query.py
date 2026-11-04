"""Typed query request/response models and route construction."""

from collections.abc import Callable

from fastapi import APIRouter
from pydantic import BaseModel, Field

from rag_anchor.api.response import ResponseResult
from rag_anchor.rag.models import QueryResult
from rag_anchor.rag.query import QueryService


class QueryRequest(BaseModel):
    """Input accepted by the query endpoint."""

    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=5)


class Citation(BaseModel):
    """A source reference attached to grounded query output."""

    document_id: str
    title: str
    source_url: str
    chunk_id: str
    position: int
    snippet: str


class QueryData(BaseModel):
    """Public query result payload."""

    answer: str | None
    citations: list[Citation]
    no_answer: bool


def _query_data(result: QueryResult) -> QueryData:
    return QueryData(
        answer=result.answer,
        citations=[
            Citation(
                document_id=item.chunk.document_id,
                title=item.chunk.title,
                source_url=item.chunk.source_url,
                chunk_id=item.chunk.chunk_id,
                position=item.chunk.position,
                snippet=item.chunk.text,
            )
            for item in result.evidence
        ],
        no_answer=result.no_answer,
    )


def create_query_router(
    query_service: QueryService,
    trace_id_factory: Callable[[], str],
) -> APIRouter:
    """Create the query router with an injected service seam."""

    router = APIRouter()

    @router.post(
        "/api/v1/query",
        response_model=ResponseResult[QueryData],
        tags=["query"],
        summary="Query the knowledge base",
        openapi_extra={"security": []},
    )
    def query(
        request: QueryRequest,
    ) -> ResponseResult[QueryData]:
        result = query_service.query(request.question, request.top_k)
        return ResponseResult(
            code=10000,
            msg="success",
            trace_id=trace_id_factory(),
            data=_query_data(result),
        )

    return router
