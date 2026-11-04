"""FastAPI application construction and the initial system endpoint."""

from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from rag_anchor.api.query import create_query_router
from rag_anchor.api.response import ResponseResult
from rag_anchor.rag.query import QueryService
from rag_anchor.rag.source import default_fixture_source


class HealthData(BaseModel):
    """Payload returned by the health endpoint."""

    status: str


def create_app(query_service: QueryService | None = None) -> FastAPI:
    """Create the RAGAnchor ASGI application."""

    application = FastAPI(title="RAGAnchor", version="0.1.0")
    service = query_service or QueryService(default_fixture_source())

    application.include_router(create_query_router(service, lambda: uuid4().hex))

    @application.get(
        "/health",
        response_model=ResponseResult[HealthData],
        tags=["system"],
        summary="Check service health",
        openapi_extra={"security": []},
    )
    def health() -> ResponseResult[HealthData]:
        """Report whether the application process is responding."""

        return ResponseResult(
            code=10000,
            msg="success",
            trace_id=uuid4().hex,
            data=HealthData(status="ok"),
        )

    return application


app = create_app()
