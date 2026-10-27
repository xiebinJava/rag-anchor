from typing import Any, Protocol, cast

from fastapi.testclient import TestClient

from rag_anchor.app import create_app


class ResponseLike(Protocol):
    status_code: int

    def json(self) -> Any: ...


class ClientLike(Protocol):
    def get(self, url: str) -> ResponseLike: ...


def test_health_returns_the_public_response_envelope() -> None:
    client = cast(ClientLike, TestClient(create_app()))

    response = client.get("/health")

    assert response.status_code == 200
    payload = cast(dict[str, Any], response.json())
    assert payload["code"] == 10000
    assert payload["msg"] == "success"
    assert payload["trace_id"]
    assert payload["data"]["status"] == "ok"
