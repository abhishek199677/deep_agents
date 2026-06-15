#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-dev}"

case "$MODE" in
    dev)
        echo "🚀 Starting development server..."
        echo "   API:  http://localhost:8000"
        echo "   Docs: http://localhost:8000/docs"
        exec uvicorn agentic.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    streamlit)
        echo "🧪 Starting Streamlit demo app..."
        exec streamlit run streamlit_app.py
        ;;
    docker)
        echo "🐳 Starting production stack via Docker Compose..."
        docker compose up --build -d
        echo "   API: http://localhost:8000"
        echo "   Running: docker compose logs -f"
        ;;
    migrate)
        echo "🗄️  Running database migration..."
        python scripts/migrate_db.py
        ;;
    *)
        echo "Usage: ./run.sh [dev|streamlit|docker|migrate]"
        exit 1
        ;;
esac