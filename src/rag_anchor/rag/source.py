"""Knowledge-source seams and the local Markdown fixture adapter."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from rag_anchor.rag.models import Document


class KnowledgeSource(Protocol):
    """Provide the documents inside the configured knowledge scope."""

    def load_documents(self) -> tuple[Document, ...]: ...


@dataclass(frozen=True, slots=True)
class MarkdownFixtureSource:
    """Load synthetic Markdown documents from one explicit directory."""

    root: Path

    def load_documents(self) -> tuple[Document, ...]:
        documents: list[Document] = []
        for path in sorted(self.root.glob("*.md")):
            content = path.read_text(encoding="utf-8").strip()
            title = self._title_for(path, content)
            documents.append(
                Document(
                    document_id=path.stem,
                    title=title,
                    source_url=f"fixture://{path.stem}",
                    content=content,
                )
            )
        return tuple(documents)

    @staticmethod
    def _title_for(path: Path, content: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line.removeprefix("# ").strip()
        raise ValueError(f"Markdown fixture has no title: {path}")


def default_fixture_source() -> MarkdownFixtureSource:
    """Build the source for the repository's synthetic knowledge fixture."""

    repository_root = Path(__file__).resolve().parents[3]
    return MarkdownFixtureSource(repository_root / "fixtures" / "knowledge")
