# This file is managed by github-config. Do not edit manually.
# https://github.com/wpfleger96/github-config

set dotenv-load := false

# Run quick quality checks (no tests)
default: sync type-check lint-check format-check

# Setup & Dependencies

# Install and sync dependencies
sync:
    uv sync

# Code Quality - Check variants

# Run mypy type checking
type-check:
    uv run mypy .

# Run linter in check mode (no fixes)
lint-check:
    uvx ruff check .

# Run formatter in check mode (no changes)
format-check:
    uvx ruff format . --check

# Code Quality - Fix variants

# Run linter and auto-fix issues
lint:
    uvx ruff check . --fix

# Run formatter and auto-fix style
format:
    uvx ruff format .

# Composite quality checks

# Run all quality checks without tests
check: sync type-check lint-check format-check
    @echo "Quick quality checks passed"

# Run all quality checks and tests
check-all: check test
    @echo "All quality checks and tests passed"

# Run pre-commit suite: lint, format, type-check, and test
pre-commit: sync type-check lint format test
    @echo "Pre-commit checks passed"

# Testing

# Run tests, excluding e2e suite
test:
    uv run pytest -m "not e2e"

# Run unit tests only
test-unit:
    uv run pytest -m unit

# Run integration tests only
test-integration:
    uv run pytest -m integration

# Run e2e tests only (no coverage)
test-e2e:
    uv run pytest -m e2e --no-cov || test $? -eq 5

# Run all tests including e2e (no coverage)
test-all:
    uv run pytest --no-cov

# Build & Package

# Build the package
build: sync
    uv build

# Remove build artifacts
clean-build:
    rm -rf dist/ build/ src/*.egg-info

# Clean and rebuild the package
rebuild: clean-build build

# Run the full CI pipeline locally
ci: sync type-check lint-check format-check test
    @echo "CI checks passed"

import? 'local.just'
