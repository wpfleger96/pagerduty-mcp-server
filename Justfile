default: sync type-check lint-check format-check

sync:
    uv sync

type-check:
    uv run mypy .

lint-check:
    uvx ruff check .

format-check:
    uvx ruff format . --check

lint:
    uvx ruff check . --fix

format:
    uvx ruff format .

check: sync type-check lint-check format-check

check-all: check test

pre-commit: sync type-check lint format test

test:
    uv run pytest

test-unit:
    uv run pytest -m unit

test-integration:
    uv run pytest -m integration

build: sync
    uv build

clean-build:
    rm -rf dist/ build/ *.egg-info

rebuild: clean-build build

ci: sync type-check lint-check format-check test
