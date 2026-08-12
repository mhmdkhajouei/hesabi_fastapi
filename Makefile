# Makefile - Hesabi Project Automation Commands

.PHONY: up down reset-db run test-concurrent clean

up:
	docker compose up -d
down:
	docker compose down
reset-db:
	docker compose down -v
	docker compose up -d
run:
	uv run uvicorn app.main:app --reload
test:
	uv run python3
stop:
	docker compose stop
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +