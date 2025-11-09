.PHONY: help install test lint security docker-build docker-up docker-down clean

help:
	@echo "SentinelVNC v2 - Makefile Commands"
	@echo ""
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run linting"
	@echo "  make security      - Run security scans"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker Compose services"
	@echo "  make docker-down   - Stop Docker Compose services"
	@echo "  make clean         - Clean temporary files"
	@echo "  make migrate       - Run database migrations"
	@echo "  make train         - Train ML models"
	@echo "  make demo          - Run complete demo"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

test:
	pytest --cov=backend --cov=detector --cov=attack_simulator --cov=merkle_anchor --cov-report=html --cov-report=term

lint:
	flake8 backend/ --max-line-length=120 --exclude=__pycache__,migrations
	pylint backend/ --disable=C0111

security:
	bandit -r backend/ -f json
	safety check

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services started. API: http://localhost:8000, Dashboard: http://localhost:8501"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-clean:
	docker-compose down -v
	docker system prune -f

migrate:
	alembic upgrade head

train:
	python train_model.py

demo:
	./run_demo.sh

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .coverage htmlcov/ .pytest_cache/

setup:
	make install
	make migrate
	make train
	@echo "Setup complete!"

