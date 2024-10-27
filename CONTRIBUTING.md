# Contributing

## Development setup

```bash
git clone https://github.com/adam-eques/langgraph-research-agent
cd langgraph-research-agent
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # fill in API keys
```

## Running tests

```bash
make test           # pytest with coverage
make lint           # ruff check
make typecheck      # mypy
```

## Commit style

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — new feature
- `fix:` — bug fix
- `refactor:` — code cleanup, no functional change
- `test:` — tests only
- `docs:` — documentation only
- `perf:` — performance improvement
- `chore:` — deps, config, CI

## Branch workflow

- All work goes on `dev`
- Open a PR against `main` when a feature is complete and tests pass
- Squash merges only — keep main history clean

## Adding a new agent

1. Create `src/research_agent/agents/my_agent.py` with a `build_my_agent_node()` function
2. Add the node to `graph.py`
3. Add routing edges
4. Add tests in `tests/test_agents.py`
