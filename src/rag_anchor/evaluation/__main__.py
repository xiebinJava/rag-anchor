"""Evaluation dataset entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rag_anchor.evaluation.models import load_evaluation_dataset
from rag_anchor.evaluation.runner import run_evaluation
from rag_anchor.rag.query import QueryService
from rag_anchor.rag.source import MarkdownFixtureSource


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the RAGAnchor evaluation dataset."
    )
    parser.add_argument(
        "--set",
        dest="dataset_path",
        required=True,
        type=Path,
        help="Path to the evaluation dataset YAML manifest.",
    )
    parser.add_argument(
        "--embedding-mode",
        choices=("lexical", "fixed_vector"),
        default=None,
        help="Override the dataset embedding mode.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional path to write the metrics JSON report.",
    )
    args = parser.parse_args(argv)
    repo_root = _repo_root()
    dataset_path = args.dataset_path
    if not dataset_path.is_absolute():
        dataset_path = repo_root / dataset_path

    dataset = load_evaluation_dataset(dataset_path, repo_root=repo_root)
    service = QueryService(MarkdownFixtureSource(dataset.knowledge_root))
    report = run_evaluation(
        dataset_path,
        service,
        embedding_mode=args.embedding_mode,
        repo_root=repo_root,
    )

    payload = report.model_dump()
    serialized = json.dumps(payload, indent=2, sort_keys=True)
    print(serialized)
    if args.json_out is not None:
        args.json_out.write_text(serialized + "\n", encoding="utf-8")

    print(
        "\nSummary: "
        f"dataset={report.dataset_version} "
        f"retriever={report.retriever_version} "
        f"failed={len(report.failed_case_ids)} "
        f"recall@{3}={report.metrics['retrieval_recall_at_3']:.3f} "
        f"citation_resolution={report.metrics['citation_resolution_rate']:.3f} "
        f"no_answer_precision={report.metrics['no_answer_precision']:.3f}"
    )

    return 1 if report.failed_case_ids else 0


if __name__ == "__main__":
    sys.exit(main())
