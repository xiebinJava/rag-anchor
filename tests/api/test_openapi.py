import json
from typing import Any, Protocol, cast

from fastapi.testclient import TestClient

from rag_anchor.app import create_app


class ResponseLike(Protocol):
    def json(self) -> Any: ...


class ClientLike(Protocol):
    def get(self, url: str) -> ResponseLike: ...


def test_openapi_documents_the_public_health_contract() -> None:
    client = cast(ClientLike, TestClient(create_app()))

    schema = cast(dict[str, Any], client.get("/openapi.json").json())
    operation = schema["paths"]["/health"]["get"]

    assert operation["tags"] == ["system"]
    assert operation["summary"] == "Check service health"
    assert operation["security"] == []

    response_schema = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]
    assert response_schema["$ref"].startswith("#/components/schemas/")
    assert "ResponseResult" in response_schema["$ref"]
    assert "#/$defs/" not in json.dumps(schema)
