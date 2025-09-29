.PHONY: dev down prod-build prod-up prod-down test test-in-container

dev-up:
	docker compose -f docker-compose.dev.yml up --build

dev-down:
	docker compose -f docker-compose.dev.yml down

prod-build:
	docker compose -f docker-compose.prod.yml build

prod-up:
	docker compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker compose -f docker-compose.prod.yml down

test: unit

unit:
	PYTHONPATH=. python -m pytest -q -m "not integration" --cov=src --cov-report=term-missing

integration:
	PYTHONPATH=. python -m pytest -q -m integration --cov=src --cov-report=term-missing

# or run tests in a fresh container
test-in-container:
	docker compose -f docker-compose.dev.yml run --rm api bash -lc "PYTHONPATH=. pytest -q --cov=src --cov-report=term-missing"