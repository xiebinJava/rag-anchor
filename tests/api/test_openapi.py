import json
from typing import Any, Protocol, cast

from fastapi.testclient import TestClient

from rag_anchor.app import create_app


class ResponseLike(Protocol):
    def json(self) -> Any: ...


class ClientLike(Protocol):
    def get(self, url: str) -> ResponseLike: ...


def resolve_local_ref(
    value: dict[str, Any], document: dict[str, Any]
) -> dict[str, Any]:
    current: Any = value
    while "$ref" in current:
        reference = cast(str, current["$ref"])
        assert reference.startswith("#/")
        target: Any = document
        for part in reference[2:].split("/"):
            target = cast(dict[str, Any], target)[part]
        current = target
    return cast(dict[str, Any], current)


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

    envelope_schema = resolve_local_ref(response_schema, schema)

    assert envelope_schema["type"] == "object"
    assert set(envelope_schema["properties"]) >= {
        "code",
        "msg",
        "trace_id",
        "data",
    }
    assert envelope_schema["properties"]["code"]["type"] == "integer"
    assert envelope_schema["properties"]["msg"]["type"] == "string"
    assert envelope_schema["properties"]["trace_id"]["type"] == "string"

    data_schema = cast(dict[str, Any], envelope_schema["properties"]["data"])
    data_branches = cast(list[dict[str, Any]], data_schema["anyOf"])
    health_ref = next(branch for branch in data_branches if "$ref" in branch)
    health_schema = resolve_local_ref(health_ref, schema)
    assert health_schema["properties"]["status"]["type"] == "string"
    assert "#/$defs/" not in json.dumps(schema)
