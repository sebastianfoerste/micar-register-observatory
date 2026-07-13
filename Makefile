.PHONY: install test refresh verify-content render

install:
	uv sync --extra dev

test:
	uv run pytest -q

refresh:
	uv run python -m observatory refresh

verify-content:
	uv run python -m observatory verify-content --limit 25

render:
	uv run python -m observatory render
