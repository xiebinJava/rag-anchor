"""Typed error responses for the public HTTP API."""

from typing import Any, cast
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from rag_anchor.api.response import ResponseResult


class ValidationIssue(BaseModel):
    """One request validation problem."""

    loc: list[str]
    msg: str
    type: str


class ValidationErrorData(BaseModel):
    """The data payload for a request validation response."""

    errors: list[ValidationIssue]


async def request_validation_exception_handler(
    _request: Request, exception: Exception
) -> JSONResponse:
    validation_error = cast(RequestValidationError, exception)
    raw_errors = cast(list[dict[str, Any]], validation_error.errors())
    issues = [
        ValidationIssue(
            loc=[str(part) for part in error["loc"]],
            msg=str(error["msg"]),
            type=str(error["type"]),
        )
        for error in raw_errors
    ]
    envelope = ResponseResult[ValidationErrorData](
        code=40001,
        msg="validation_error",
        trace_id=uuid4().hex,
        data=ValidationErrorData(errors=issues),
    )
    return JSONResponse(status_code=422, content=envelope.model_dump(mode="json"))


def register_error_handlers(application: FastAPI) -> None:
    """Register stable error responses on an application instance."""

    application.add_exception_handler(
        RequestValidationError,
        request_validation_exception_handler,
    )
