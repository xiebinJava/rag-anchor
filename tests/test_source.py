from pathlib import Path

import pytest

from rag_anchor.rag.source import MarkdownFixtureSource


def test_markdown_fixture_requires_a_title(tmp_path: Path) -> None:
    fixture = tmp_path / "malformed.md"
    fixture.write_text("This fixture has no heading.", encoding="utf-8")

    with pytest.raises(ValueError, match="has no title"):
        MarkdownFixtureSource(tmp_path).load_documents()


def test_markdown_fixture_requires_an_existing_directory(tmp_path: Path) -> None:
    missing_root = tmp_path / "missing"

    with pytest.raises(FileNotFoundError, match="Fixture root does not exist"):
        MarkdownFixtureSource(missing_root).load_documents()
