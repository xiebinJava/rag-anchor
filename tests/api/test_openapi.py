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


def assert_local_refs_resolve(value: Any, document: dict[str, Any]) -> None:
    if isinstance(value, dict):
        if "$ref" in value:
            resolve_local_ref(cast(dict[str, Any], value), document)
        typed_value = cast(dict[str, Any], value)
        for child in typed_value.values():
            assert_local_refs_resolve(child, document)
    elif isinstance(value, list):
        for child in cast(list[Any], value):
            assert_local_refs_resolve(child, document)


def test_openapi_documents_the_public_health_contract() -> None:
    client = cast(ClientLike, TestClient(create_app()))

    schema = cast(dict[str, Any], client.get("/openapi.json").json())
    assert_local_refs_resolve(schema, schema)
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


def test_openapi_documents_the_query_contract() -> None:
    client = cast(ClientLike, TestClient(create_app()))

    schema = cast(dict[str, Any], client.get("/openapi.json").json())
    assert_local_refs_resolve(schema, schema)
    operation = schema["paths"]["/api/v1/query"]["post"]

    assert operation["tags"] == ["query"]
    assert operation["summary"] == "Query the knowledge base"
    assert operation["security"] == []

    request_schema = resolve_local_ref(
        operation["requestBody"]["content"]["application/json"]["schema"],
        schema,
    )
    assert set(request_schema["properties"]) >= {"question", "top_k"}
    assert request_schema["properties"]["question"]["minLength"] == 1
    assert request_schema["properties"]["question"]["maxLength"] == 2000
    assert request_schema["properties"]["top_k"]["minimum"] == 1
    assert request_schema["properties"]["top_k"]["maximum"] == 5

    response_schema = resolve_local_ref(
        operation["responses"]["200"]["content"]["application/json"]["schema"],
        schema,
    )
    assert set(response_schema["properties"]) >= {
        "code",
        "msg",
        "trace_id",
        "data",
    }
    query_data_schema = resolve_local_ref(
        next(
            branch
            for branch in response_schema["properties"]["data"]["anyOf"]
            if "$ref" in branch
        ),
        schema,
    )
    assert set(query_data_schema["properties"]) == {
        "answer",
        "citations",
        "no_answer",
    }
    citation_schema = resolve_local_ref(
        query_data_schema["properties"]["citations"]["items"],
        schema,
    )
    assert set(citation_schema["properties"]) == {
        "document_id",
        "title",
        "source_url",
        "chunk_id",
        "position",
        "snippet",
    }

    validation_response = resolve_local_ref(
        operation["responses"]["422"]["content"]["application/json"]["schema"],
        schema,
    )
    validation_data = resolve_local_ref(
        next(
            branch
            for branch in validation_response["properties"]["data"]["anyOf"]
            if "$ref" in branch
        ),
        schema,
    )
    assert set(validation_data["properties"]) == {"errors"}
    validation_issue = resolve_local_ref(
        validation_data["properties"]["errors"]["items"],
        schema,
    )
    assert set(validation_issue["properties"]) == {"loc", "msg", "type"}
