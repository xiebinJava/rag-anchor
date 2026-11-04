"""Markdown fixture knowledge source."""

from __future__ import annotations

import re
from pathlib import Path

from rag_anchor.rag.models import ChunkRecord, DocumentRecord

_HEADING_PATTERN = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def _split_sections(markdown: str) -> tuple[tuple[str, str], ...]:
    matches = list(_HEADING_PATTERN.finditer(markdown))
    if not matches:
        body = markdown.strip()
        if not body:
            return ()
        return (("body", body),)

    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        text = markdown[start:end].strip()
        if text:
            sections.append((heading, text))
    return tuple(sections)


class MarkdownFixtureSource:
    """Load synthetic markdown documents from a bound fixture root."""

    def __init__(self, root: Path) -> None:
        self._root = root

    @property
    def root(self) -> Path:
        return self._root

    def load_documents(self) -> tuple[DocumentRecord, ...]:
        if not self._root.is_dir():
            msg = f"fixture root does not exist: {self._root}"
            raise FileNotFoundError(msg)

        documents: list[DocumentRecord] = []
        for path in sorted(self._root.glob("*.md")):
            document_id = path.stem
            markdown = path.read_text(encoding="utf-8")
            title_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else document_id
            sections = _split_sections(markdown)
            chunks: list[ChunkRecord] = []
            revision_id = f"revision-{document_id}"
            source_url = f"fixture://{self._root.name}/{path.name}"
            for position, (heading, text) in enumerate(sections):
                chunk_id = f"{document_id}:{position}"
                chunks.append(
                    ChunkRecord(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        revision_id=revision_id,
                        title=title,
                        source_url=source_url,
                        text=f"{heading}\n{text}",
                        position=position,
                    )
                )
            documents.append(
                DocumentRecord(
                    document_id=document_id,
                    revision_id=revision_id,
                    title=title,
                    source_url=source_url,
                    chunks=tuple(chunks),
                    metadata={"heading": title},
                )
            )
        return tuple(documents)

    def chunk_index(self) -> dict[str, ChunkRecord]:
        index: dict[str, ChunkRecord] = {}
        for document in self.load_documents():
            for chunk in document.chunks:
                index[chunk.chunk_id] = chunk
        return index
