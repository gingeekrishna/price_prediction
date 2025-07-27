# Makefile for Vehicle Price Prediction Project
# Provides common development tasks and shortcuts

.PHONY: help install test lint format clean run docker-build docker-run

# Default target
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run test suite"
	@echo "  test-cov    - Run tests with coverage"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code with black and isort"
	@echo "  type-check  - Run type checking with mypy"
	@echo "  clean       - Clean up temporary files"
	@echo "  run         - Start the API server"
	@echo "  run-demo    - Run the demo agent"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run Docker container"
	@echo "  logs        - View prediction logs"
	@echo "  train       - Train new model"

# Installation and setup
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pre-commit
	pre-commit install

# Testing
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-unit:
	pytest tests/ -v -m "unit"

test-integration:
	pytest tests/ -v -m "integration"

test-parallel:
	pytest tests/ -v -n auto

# Code quality
lint:
	flake8 src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/

# Cleaning
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build/

# Application commands
run:
	uvicorn src.api:app --reload --host 0.0.0.0 --port 8000

run-demo:
	python -m src.demo_agent

logs:
	python logs/view_logs.py --limit 20 --summary

logs-export:
	python logs/view_logs.py --export predictions_export.csv

train:
	python scripts/train_model.py

# Docker commands
docker-build:
	docker build -t vehicle-price-prediction .

docker-run:
	docker run -p 8000:8000 vehicle-price-prediction

docker-shell:
	docker run -it vehicle-price-prediction /bin/bash

# Database commands
init-db:
	python -c "from src.api import init_db; init_db()"

reset-db:
	rm -f predictions.db
	python -c "from src.api import init_db; init_db()"

# Development helpers
dev-setup: install-dev init-db
	@echo "Development environment setup complete!"

check-all: format lint type-check test
	@echo "All checks passed!"

# Production commands
deploy-check: clean install test lint type-check
	@echo "Deployment checks passed!"

# Environment management
create-env:
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  Linux/Mac: source venv/bin/activate"

# Documentation
docs:
	@echo "Starting API documentation server..."
	@echo "Visit: http://localhost:8000/docs"
	uvicorn src.api:app --reload

# Performance testing
perf-test:
	@echo "Running performance tests..."
	pytest tests/ -v -m "slow"

# Security checks
security-check:
	bandit -r src/
	safety check

# Full CI pipeline simulation
ci: clean install lint type-check test-cov
	@echo "CI pipeline simulation complete!"
