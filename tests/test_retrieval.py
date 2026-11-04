from rag_anchor.rag.models import Document
from rag_anchor.rag.retrieval import chunk_documents


def test_chunking_preserves_body_text_after_a_markdown_heading() -> None:
    document = Document(
        document_id="heading-adjacency",
        title="Heading adjacency",
        source_url="fixture://heading-adjacency",
        content="# Heading\nPostgreSQL is used here.",
    )

    chunks = chunk_documents((document,))

    assert [chunk.text for chunk in chunks] == ["PostgreSQL is used here."]
