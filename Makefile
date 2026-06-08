.PHONY: dev build up down logs migrate shell clean

# ─── Development ───────────────────────────────────────────

dev:
	uvicorn agentic.main:app --reload --host 0.0.0.0 --port 8000

shell:
	ipython

# ─── Docker ────────────────────────────────────────────────

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart: down up

# ─── Database ──────────────────────────────────────────────

migrate:
	python scripts/migrate_db.py

reset-db:
	docker compose down -v
	docker compose up -d postgres redis
	sleep 5
	python scripts/migrate_db.py

# ─── Production helpers ────────────────────────────────────

health:
	curl -s http://localhost:8000/health | jq .

shell-api:
	docker compose exec api bash

shell-db:
	docker compose exec postgres psql -U agentic agentic

# ─── Cleanup ───────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
