"""Stable response models for the public HTTP API."""

from typing import TypeVar

from pydantic import BaseModel

ResponseDataT = TypeVar("ResponseDataT")


class ResponseResult[ResponseDataT](BaseModel):
    """The response envelope shared by public API routes."""

    code: int
    msg: str
    trace_id: str
    data: ResponseDataT | None = None
