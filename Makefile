.PHONY: help install dev test lint type-check clean db-up db-down db-restart run

help:
	@echo "Available commands:"
	@echo "  install      Install production dependencies"
	@echo "  dev          Install development dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run Ruff linter"
	@echo "  type-check   Run mypy type checking"
	@echo "  clean        Clean cache files"
	@echo "  db-up        Start PostgreSQL"
	@echo "  db-down      Stop PostgreSQL"
	@echo "  db-restart   Restart PostgreSQL"
	@echo "  run          Run ETL pipeline"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest tests/ -v --cov=src/ecommerce_pipeline

lint:
	ruff check src/ tests/

type-check:
	mypy src/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

db-up:
	docker-compose up -d postgres

db-down:
	docker-compose down

db-restart: db-down db-up

run:
	python -m src.ecommerce_pipeline.pipeline data/samples/orders.csv