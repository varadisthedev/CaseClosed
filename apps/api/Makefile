.PHONY: install dev migrate migrate-create seed test lint

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(MSG)"

seed:
	python -m scripts.seed_case_pack

test:
	pytest -v

lint:
	ruff check .