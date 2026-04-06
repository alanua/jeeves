.PHONY: install dev up down logs migrate test lint format

install:
	pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(msg)"

test:
	pytest -v

lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/
	black app/ tests/

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

validate:
	python scripts/validate.py
