.PHONY: help up down dev test lint typecheck fmt install clean

help:
	@echo "Raw — common commands:"
	@echo "  make install   install backend deps (uv)"
	@echo "  make up         start postgres + redis (docker compose)"
	@echo "  make down       stop infra"
	@echo "  make dev        run the backend API"
	@echo "  make test       run tests"
	@echo "  make lint       ruff + mypy"
	@echo "  make fmt        auto-format (ruff)"

install:
	cd apps/backend && uv sync

up:
	docker compose up -d postgres redis

down:
	docker compose down

dev:
	cd apps/backend && uv run uvicorn raw.main:app --reload --host 127.0.0.1 --port 8077

test:
	cd apps/backend && uv run pytest -q

lint:
	cd apps/backend && uv run ruff check . && uv run mypy src

fmt:
	cd apps/backend && uv run ruff format . && uv run ruff check --fix .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
