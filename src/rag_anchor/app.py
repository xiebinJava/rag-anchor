"""FastAPI application construction and the initial system endpoint."""

from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from rag_anchor.api.response import ResponseResult


class HealthData(BaseModel):
    """Payload returned by the health endpoint."""

    status: str


def create_app() -> FastAPI:
    """Create the RAGAnchor ASGI application."""

    application = FastAPI(title="RAGAnchor", version="0.1.0")

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
