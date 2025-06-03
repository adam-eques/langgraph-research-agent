# ============================================================
# LangGraph Research Agent — Makefile
# ============================================================

.PHONY: install test lint format serve docker-build docker-up docker-down \
        index evaluate clean help

PYTHON        ?= python
PIP           ?= pip
SRC_DIRS      := src tests scripts examples
COLLECTION    ?= research_docs
DOCS_DIR      ?= ./docs

# ============================================================
# Development setup
# ============================================================

## install: Install the package and all development/test dependencies
install:
	$(PIP) install -e ".[dev,test]"

## install-extras: Install optional heavy extras (sentence-transformers, fpdf2, etc.)
install-extras:
	$(PIP) install sentence-transformers rank-bm25 fpdf2 redis tqdm nltk prometheus-client

# ============================================================
# Quality gates
# ============================================================

## lint: Run ruff linter on all source files
lint:
	ruff check $(SRC_DIRS) --output-format=concise

## format: Auto-format source files with ruff
format:
	ruff format $(SRC_DIRS)
	ruff check --fix $(SRC_DIRS)

## typecheck: Run mypy static type checks
typecheck:
	mypy src/research_agent --ignore-missing-imports --no-strict-optional

## test: Run the full test suite with coverage
test:
	pytest tests/ \
		--cov=research_agent \
		--cov-report=term-missing \
		--cov-report=html \
		-v \
		--tb=short

## test-fast: Run tests without coverage (faster feedback loop)
test-fast:
	pytest tests/ -v --tb=short -x

## test-unit: Run only fast unit tests (no slow integration tests)
test-unit:
	pytest tests/ -v --tb=short -m "not slow"

# ============================================================
# Running the application
# ============================================================

## serve: Start the FastAPI research agent server (development mode)
serve:
	uvicorn research_agent.api:app --reload --host 0.0.0.0 --port 8000

## serve-prod: Start the server in production mode (no reload)
serve-prod:
	uvicorn research_agent.api:app --host 0.0.0.0 --port 8000 --workers 4

# ============================================================
# Docker operations
# ============================================================

## docker-build: Build the Docker image
docker-build:
	docker build -t research-agent:latest .

## docker-up: Start all services with docker-compose
docker-up:
	docker compose up -d
	@echo "Services started. API available at http://localhost:8000"
	@echo "ChromaDB available at http://localhost:8001"

## docker-down: Stop and remove all docker-compose services
docker-down:
	docker compose down

## docker-logs: Follow logs from all services
docker-logs:
	docker compose logs -f

## docker-restart: Restart the app service only
docker-restart:
	docker compose restart app

## docker-shell: Open a shell in the running app container
docker-shell:
	docker compose exec app /bin/bash

# ============================================================
# Document indexing
# ============================================================

## index: Index documents from DOCS_DIR into the vector store
## Usage: make index DOCS_DIR=./my-docs COLLECTION=my_collection
index:
	$(PYTHON) scripts/ingest.py $(DOCS_DIR) --collection $(COLLECTION) --recursive

## index-file: Index a single file
## Usage: make index-file FILE=./doc.pdf
index-file:
	$(PYTHON) scripts/ingest.py $(FILE) --collection $(COLLECTION)

# ============================================================
# Evaluation
# ============================================================

## evaluate: Run the evaluation harness on a dataset
## Usage: make evaluate DATASET=./eval/dataset.json
evaluate:
	$(PYTHON) -c "\
import json, sys; \
from research_agent.eval.harness import EvalHarness; \
from research_agent.logging_config import setup_logging; \
setup_logging(); \
dataset = json.load(open('$(DATASET)')); \
harness = EvalHarness(); \
report = harness.run(dataset); \
print(report.summary())"

# ============================================================
# Cache management
# ============================================================

## clear-cache: Clear the research result cache
clear-cache:
	research-agent clear-cache

# ============================================================
# Cleanup
# ============================================================

## clean: Remove Python cache files, build artifacts, and test outputs
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ coverage.xml .coverage dist/ build/
	@echo "Cleaned build artifacts"

## clean-docker: Remove Docker volumes (WARNING: deletes all vector store data)
clean-docker:
	docker compose down -v
	@echo "Docker volumes removed"

# ============================================================
# Help
# ============================================================

## help: Show this help message
help:
	@echo "LangGraph Research Agent — available targets:"
	@echo ""
	@grep -E '^## ' Makefile | sed 's/## /  /' | column -t -s ':'
	@echo ""
	@echo "Variables:"
	@echo "  DOCS_DIR    Directory to index (default: ./docs)"
	@echo "  COLLECTION  Chroma collection name (default: research_docs)"
	@echo "  DATASET     Path to eval dataset JSON (required for 'evaluate')"

.DEFAULT_GOAL := help
