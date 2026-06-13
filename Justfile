# This file is managed by github-config. Do not edit manually.
# https://github.com/wpfleger96/github-config

# Settings
set dotenv-load := false

# Default recipe: quick quality check without tests
default: sync type-check lint-check format-check

# Setup & Dependencies
sync:
    uv sync

# Code Quality - Check variants
type-check:
    uv run mypy .

lint-check:
    uvx ruff check .

format-check:
    uvx ruff format . --check

# Code Quality - Fix variants
lint:
    uvx ruff check . --fix

format:
    uvx ruff format .

# Composite quality checks
check: sync type-check lint-check format-check
    @echo "Quick quality checks passed"

check-all: check test
    @echo "All quality checks and tests passed"

pre-commit: sync type-check lint format test
    @echo "Pre-commit checks passed"

# Testing
# Default `test` excludes the e2e suite (run separately via `test-e2e`).
test:
    uv run pytest -m "not e2e"

test-unit:
    uv run pytest -m unit

test-integration:
    uv run pytest -m integration

test-e2e:
    uv run pytest -m e2e --no-cov || test $? -eq 5

# Everything, including the e2e suite.
test-all:
    uv run pytest --no-cov

# Build & Package
build: sync
    uv build

clean-build:
    rm -rf dist/ build/ src/*.egg-info

rebuild: clean-build build

# CI workflow (matches CI steps)
ci: sync type-check lint-check format-check test
    @echo "CI checks passed"

import? 'local.just'
