#!/usr/bin/env python3
"""Bulk-index documents from a directory into the research agent vector store.

Usage examples:

    python scripts/ingest.py ./docs/ --collection research_docs --recursive
    python scripts/ingest.py ./paper.pdf --collection papers
    python scripts/ingest.py ./docs/ --dry-run  # preview without indexing
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure the src/ directory is on the path when running as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from research_agent.logging_config import setup_logging

logger = logging.getLogger(__name__)

_SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def _collect_files(target: Path, recursive: bool) -> list[Path]:
    """Return all supported files under *target* (file or directory)."""
    if target.is_file():
        if target.suffix in _SUPPORTED_EXTENSIONS:
            return [target]
        print(f"Warning: {target.name} has unsupported extension {target.suffix!r} — skipping")
        return []

    if not target.is_dir():
        print(f"Error: {target} is neither a file nor a directory")
        sys.exit(1)

    if recursive:
        files = [f for f in target.rglob("*") if f.is_file() and f.suffix in _SUPPORTED_EXTENSIONS]
    else:
        files = [f for f in target.iterdir() if f.is_file() and f.suffix in _SUPPORTED_EXTENSIONS]

    # Sort for deterministic order
    return sorted(files)


def main() -> None:
    setup_logging()

    parser = argparse.ArgumentParser(
        description="Bulk-index documents into the research agent vector store.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "path",
        type=Path,
        help="File or directory to index",
    )
    parser.add_argument(
        "--collection",
        default="",
        help="Chroma collection name (defaults to CHROMA_COLLECTION env var or 'research_docs')",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=False,
        help="Recursively traverse subdirectories",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview which files would be indexed without actually indexing them",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of files to index in each progress-bar batch (default: 10)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable debug logging",
    )
    args = parser.parse_args()

    if args.verbose:
        setup_logging(level="DEBUG")

    # --- Collect files ---
    files = _collect_files(args.path, args.recursive)

    if not files:
        print(
            "No supported files found. Supported extensions:",
            ", ".join(sorted(_SUPPORTED_EXTENSIONS)),
        )
        sys.exit(0)

    print(f"Found {len(files)} file(s) to index")

    if args.dry_run:
        print("\nDRY RUN — no files will be indexed:\n")
        for f in files:
            print(f"  {f}")
        sys.exit(0)

    # --- Import indexing deps after argument parsing so --help is fast ---
    from research_agent.config import config as cfg
    from research_agent.rag.retriever import index_document

    collection = args.collection or cfg.chroma_collection
    print(f"Indexing into collection: {collection!r}\n")

    # --- Try to use tqdm for progress bar; fall back to plain output ---
    try:
        from tqdm import tqdm  # type: ignore[import-untyped]

        iterator = tqdm(files, desc="Indexing", unit="file", dynamic_ncols=True)
    except ImportError:
        iterator = files  # type: ignore[assignment]

    indexed_count = 0
    failed_count = 0
    failed_files: list[tuple[Path, str]] = []

    for file_path in iterator:
        try:
            chunk_count = index_document(file_path, collection=collection)
            indexed_count += 1
            logger.debug("Indexed %s (%d chunks)", file_path.name, chunk_count)
        except Exception as exc:
            failed_count += 1
            failed_files.append((file_path, str(exc)))
            logger.error("Failed to index %s: %s", file_path.name, exc)

    # --- Summary ---
    print(f"\n{'=' * 50}")
    print("Indexing complete")
    print(f"  Indexed:  {indexed_count} / {len(files)} files")
    print(f"  Failed:   {failed_count} file(s)")
    if failed_files:
        print("\nFailed files:")
        for path, reason in failed_files:
            print(f"  {path.name}: {reason}")

    if failed_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
