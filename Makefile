.PHONY: install test refresh render report freshness

install:
	uv sync --extra dev

test:
	uv run pytest -q

refresh:
	uv run python -m observatory refresh

render:
	uv run python -m observatory render

report:
	uv run python -m report build

freshness:
	uv run python scripts/check_snapshot_freshness.py
