.PHONY: install test build

install:
	uv sync --extra dev

test:
	uv run pytest -q

build:
	uv run python -m report build
