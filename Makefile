.PHONY: help install test lint coverage up down clean setup seed

help:
	@echo "SentinelVNC - Makefile Commands"
	@echo ""
	@echo "  make install   - Install dependencies"
	@echo "  make test      - Run tests with coverage"
	@echo "  make lint      - Run linting"
	@echo "  make coverage  - Run tests and show coverage report"
	@echo "  make up        - Start Docker Compose services"
	@echo "  make down      - Stop Docker Compose services"
	@echo "  make clean     - Clean temporary files"
	@echo "  make setup     - Full setup (install, seed, train)"
	@echo "  make seed      - Seed sample data"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-asyncio

test:
	pytest --cov=backend --cov=dashboard --cov=attack_simulator --cov-report=term --cov-report=html

coverage:
	pytest --cov=backend --cov=dashboard --cov=attack_simulator --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running flake8..."
	@flake8 backend/ dashboard/ attack_simulator/ --max-line-length=120 --exclude=__pycache__,migrations || true
	@echo "Running pylint..."
	@pylint backend/ --disable=C0111,R0903 || true

up:
	cd infra && docker-compose up --build -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services started!"
	@echo "  API: http://localhost:8000"
	@echo "  Dashboard: http://localhost:8501"
	@echo "  API Docs: http://localhost:8000/docs"

down:
	cd infra && docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/ .tox/ dist/ build/

seed:
	python scripts/seed_data.py

setup: install seed
	@echo "Setup complete! Run 'make up' to start services."

