from typing import Any, NoReturn, Protocol, cast

from fastapi.testclient import TestClient
from pytest import mark

from rag_anchor.app import create_app
from rag_anchor.rag.query import QueryService


class ResponseLike(Protocol):
    status_code: int

    def json(self) -> Any: ...


class ClientLike(Protocol):
    def post(self, url: str, json: dict[str, Any]) -> ResponseLike: ...


class RejectingQueryService:
    def query(self, question: str, top_k: int) -> NoReturn:
        del question, top_k
        raise AssertionError("whitespace-only input reached query service")


def test_query_returns_grounded_answer_and_citation() -> None:
    client = cast(ClientLike, TestClient(create_app()))

    response = client.post(
        "/api/v1/query",
        json={"question": "Which database does RAGAnchor use?"},
    )

    assert response.status_code == 200
    payload = cast(dict[str, Any], response.json())
    assert payload["code"] == 10000
    assert payload["trace_id"]
    assert payload["data"]["no_answer"] is False
    assert "PostgreSQL" in payload["data"]["answer"]

    citation = payload["data"]["citations"][0]
    assert citation["document_id"] == "rag-anchor-baseline"
    assert citation["source_url"] == "fixture://rag-anchor-baseline"


def test_query_returns_no_answer_without_matching_evidence() -> None:
    client = cast(ClientLike, TestClient(create_app()))

    response = client.post(
        "/api/v1/query",
        json={"question": "What is the launch code for the moon base?"},
    )

    assert response.status_code == 200
    payload = cast(dict[str, Any], response.json())
    assert payload["data"] == {
        "answer": None,
        "citations": [],
        "no_answer": True,
    }


def test_query_respects_top_k_for_returned_citations() -> None:
    client = cast(ClientLike, TestClient(create_app()))

    response = client.post(
        "/api/v1/query",
        json={"question": "RAGAnchor citations", "top_k": 1},
    )

    assert response.status_code == 200
    payload = cast(dict[str, Any], response.json())
    assert len(payload["data"]["citations"]) == 1


def test_query_rejects_whitespace_only_before_service_call() -> None:
    app = create_app(cast(QueryService, RejectingQueryService()))
    client = cast(ClientLike, TestClient(app))

    response = client.post("/api/v1/query", json={"question": " \t\n"})

    assert response.status_code == 422


@mark.parametrize(
    "request_body",
    [
        {"question": ""},
        {"question": "database", "top_k": 0},
        {"question": "database", "top_k": 6},
        {"question": "x" * 2001},
    ],
)
def test_query_rejects_invalid_request(request_body: dict[str, Any]) -> None:
    client = cast(ClientLike, TestClient(create_app()))

    response = client.post("/api/v1/query", json=request_body)

    assert response.status_code == 422
    payload = cast(dict[str, Any], response.json())
    assert payload["code"] == 40001
    assert payload["msg"] == "validation_error"
    assert payload["trace_id"]
    assert payload["data"]["errors"]
