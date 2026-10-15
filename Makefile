.PHONY: install test lint typecheck check refresh render report freshness

install:
	uv sync --extra dev

test:
	uv run pytest -q

lint:
	uv run ruff check .

typecheck:
	uv run mypy

check: lint typecheck test

refresh:
	uv run python -m observatory refresh

render:
	uv run python -m observatory render

report:
	uv run python -m report build

freshness:
	uv run python scripts/check_snapshot_freshness.py
