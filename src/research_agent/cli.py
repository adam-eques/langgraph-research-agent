"""Click-based CLI for the research agent."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import click

# Rich is optional — fall back to plain print if absent.
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn

    _console = Console()

    def _print(text: str) -> None:
        _console.print(text)

    def _print_md(text: str) -> None:
        _console.print(Markdown(text))

    def _print_panel(text: str, title: str = "") -> None:
        _console.print(Panel(text, title=title, expand=False))

    def _spinner(description: str):
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )

    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

    def _print(text: str) -> None:  # type: ignore[misc]
        print(text)

    def _print_md(text: str) -> None:  # type: ignore[misc]
        print(text)

    def _print_panel(text: str, title: str = "") -> None:  # type: ignore[misc]
        if title:
            print(f"\n=== {title} ===")
        print(text)

    class _spinner:  # type: ignore[misc]  # noqa: N801  # mirrors the _spinner() fallback above
        def __init__(self, description: str) -> None:
            self._desc = description

        def __enter__(self) -> _spinner:
            print(f"{self._desc}...", flush=True)
            return self

        def add_task(self, *args: Any, **kwargs: Any) -> None:
            pass

        def __exit__(self, *args: Any) -> None:
            pass


@click.group()
@click.version_option(package_name="research-agent")
def cli() -> None:
    """LangGraph multi-agent research assistant CLI."""


# ---------------------------------------------------------------------------
# research command
# ---------------------------------------------------------------------------


@cli.command()
@click.argument("query")
@click.option(
    "--stream",
    is_flag=True,
    default=False,
    help="Stream tokens as they are generated instead of waiting for the full answer.",
)
@click.option(
    "--supervisor",
    is_flag=True,
    default=False,
    help="Enable supervisor mode (dynamic routing).",
)
@click.option(
    "--session-id",
    default="",
    help="Session ID for conversation memory.",
)
def research(query: str, stream: bool, supervisor: bool, session_id: str) -> None:
    """Run a research query and print the answer.

    QUERY is the research question to answer.

    Examples:

    \b
      research-agent research "What is retrieval augmented generation?"
      research-agent research --stream "Latest advances in LLM agents"
    """
    from research_agent.logging_config import setup_logging

    setup_logging()

    if stream:
        _run_stream(query)
    else:
        _run_sync(query, use_supervisor=supervisor)


def _run_sync(query: str, use_supervisor: bool = False) -> None:
    from research_agent.graph import build_graph
    from research_agent.state import ResearchState

    if _HAS_RICH:
        progress = Progress(SpinnerColumn(), TextColumn("{task.description}"), transient=True)
        with progress:
            progress.add_task("Researching...", total=None)
            graph = build_graph(use_supervisor=use_supervisor)
            initial: ResearchState = {
                "messages": [],
                "query": query,
                "research_notes": [],
                "document_context": "",
                "citations": [],
                "next": "",
            }
            result = graph.invoke(initial)
    else:
        print("Researching... (this may take a minute)", flush=True)
        graph = build_graph(use_supervisor=use_supervisor)
        initial = {
            "messages": [],
            "query": query,
            "research_notes": [],
            "document_context": "",
            "citations": [],
            "next": "",
        }
        result = graph.invoke(initial)

    messages = list(result.get("messages", []))
    answer = ""
    for msg in reversed(messages):
        if hasattr(msg, "content") and msg.content:
            answer = str(msg.content)
            break

    _print_panel(
        f"[bold]Query:[/bold] {query}" if _HAS_RICH else f"Query: {query}", title="Research Result"
    )
    _print_md(answer)

    notes = result.get("research_notes", [])
    if notes:
        _print("\n[dim]Research notes:[/dim]" if _HAS_RICH else "\nResearch notes:")
        for note in notes[:5]:
            _print(f"  • {note[:120]}")


def _run_stream(query: str) -> None:
    from research_agent.streaming import stream_tokens

    _print(f"Streaming answer for: {query}\n")
    try:
        for token in stream_tokens(query):
            print(token, end="", flush=True)
        print()  # final newline
    except KeyboardInterrupt:
        print("\n[interrupted]")
        sys.exit(0)


# ---------------------------------------------------------------------------
# index command
# ---------------------------------------------------------------------------


@cli.command(name="index")
@click.argument("path", type=click.Path(exists=True))
@click.option("--collection", default="", help="Chroma collection name (overrides env var).")
@click.option(
    "--recursive",
    is_flag=True,
    default=False,
    help="Recursively index all supported files under PATH.",
)
def index_command(path: str, collection: str, recursive: bool) -> None:
    """Index a document (or directory) into the vector store.

    PATH is a file or directory to index.

    Examples:

    \b
      research-agent index ./docs/report.pdf
      research-agent index ./docs/ --recursive --collection my_docs
    """
    from research_agent.config import config as cfg
    from research_agent.rag.retriever import index_document

    coll = collection or cfg.chroma_collection
    target = Path(path)

    if target.is_file():
        files = [target]
    elif recursive:
        supported = {".pdf", ".docx", ".txt", ".md"}
        files = [f for f in target.rglob("*") if f.suffix in supported]
    else:
        supported = {".pdf", ".docx", ".txt", ".md"}
        files = [f for f in target.iterdir() if f.suffix in supported]

    if not files:
        _print("No supported files found.")
        sys.exit(1)

    _print(f"Indexing {len(files)} file(s) into collection '{coll}'...")
    indexed = 0
    failed = 0
    for f in files:
        try:
            count = index_document(f, collection=coll)
            _print(
                f"  [green]OK[/green]  {f.name} ({count} chunks)"
                if _HAS_RICH
                else f"  OK  {f.name} ({count} chunks)"
            )
            indexed += 1
        except Exception as exc:
            _print(
                f"  [red]FAIL[/red] {f.name} — {exc}" if _HAS_RICH else f"  FAIL {f.name} — {exc}"
            )
            failed += 1

    _print(f"\nDone. Indexed: {indexed}, Failed: {failed}")


# ---------------------------------------------------------------------------
# serve command
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--host", default="0.0.0.0", show_default=True, help="Bind host.")
@click.option("--port", default=8000, show_default=True, type=int, help="Bind port.")
@click.option(
    "--reload",
    is_flag=True,
    default=False,
    help="Enable auto-reload (development only).",
)
@click.option(
    "--workers", default=1, show_default=True, type=int, help="Number of worker processes."
)
def serve(host: str, port: int, reload: bool, workers: int) -> None:
    """Start the FastAPI research agent server.

    Example:

    \b
      research-agent serve --port 8080
      research-agent serve --reload
    """
    try:
        import uvicorn  # type: ignore[import-untyped]
    except ImportError:
        click.echo("uvicorn is required to run the server: pip install uvicorn[standard]")
        sys.exit(1)

    _print(f"Starting server on http://{host}:{port}")
    uvicorn.run(
        "research_agent.api:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level="info",
    )


# ---------------------------------------------------------------------------
# clear-cache command
# ---------------------------------------------------------------------------


@cli.command(name="clear-cache")
@click.confirmation_option(prompt="This will clear all cached research results. Continue?")
def clear_cache() -> None:
    """Clear the result cache (both in-memory and Redis, depending on config)."""
    from research_agent.cache import ResultCache

    cache = ResultCache()
    cache.clear()
    _print(
        "[green]Cache cleared successfully.[/green]" if _HAS_RICH else "Cache cleared successfully."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Package entry point called by ``research-agent`` console script."""
    cli()


if __name__ == "__main__":
    main()
