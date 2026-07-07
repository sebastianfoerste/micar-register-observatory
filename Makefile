.PHONY: install test refresh render

install:
	uv sync --extra dev

test:
	uv run pytest -q

refresh:
	uv run python -m observatory refresh

render:
	uv run python -m observatory render
