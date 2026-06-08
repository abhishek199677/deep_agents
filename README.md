# Deep Agents — Production-Grade Agentic AI Platform

Build and deploy autonomous AI agents powered by LangGraph + `deepagents`, with planning, web search, subagents, skills, and persistent storage.

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌──────────────┐     ┌─────────────┐
│  React/     │────▶│  Nginx   │────▶│  FastAPI     │────▶│  Deep Agent │
│  Next.js    │     │  (proxy) │     │  (API server)│     │  (LangGraph)│
│  (or any    │◀────│          │◀────│              │◀────│             │
│   client)   │     └──────────┘     └──────┬───────┘     └──────┬──────┘
└─────────────┘                             │                    │
                                     ┌──────┴───────┐     ┌──────┴──────┐
                                     │   Redis       │     │  PostgreSQL │
                                     │  (cache,      │     │  (threads,  │
                                     │   rate limit) │     │   store)    │
                                     └──────────────┘     └─────────────┘
```

## Quick Start

```bash
# Development (FastAPI hot-reload)
./run.sh dev
# → http://localhost:8000/docs

# Streamlit demo app
./run.sh streamlit

# Full production stack
./run.sh docker
```

## Project Structure

```
agentic/                  # Production backend package
├── main.py               # FastAPI app (entry point)
├── config.py             # Pydantic Settings (env loading)
├── agent_factory.py      # Deep agent builder
├── schemas.py            # Pydantic request/response models
├── auth.py               # JWT authentication
├── rate_limit.py         # Rate limiter
├── logging_config.py     # Structured logging (structlog)
└── routes/
    ├── health.py         # Health check endpoints
    └── chat.py           # Chat + WebSocket streaming

deepagentsdemo/           # Original course notebooks (dev only)
├── 1-basicsdeepagent.ipynb
├── 2-contextengineering.ipynb
├── 3-backends.ipynb
├── 4-subagents.ipynb
├── skills/               # Agent skills
├── projects/AGENTS.md    # Context engineering file
└── .env                  # Local config (gitignored)

streamlit_app.py          # Demo UI (educational use)
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness probe |
| POST | `/api/v1/chat` | Send message, get response |
| WS | `/api/v1/ws/{thread_id}` | Stream agent execution in real-time |

## Deployment

```bash
# 1. Set secrets in your environment
export OPENAI_API_KEY="sk-..."
export TAVILY_API_KEY="tvly-..."
export JWT_SECRET="$(openssl rand -hex 32)"

# 2. Run migration
python scripts/migrate_db.py

# 3. Launch
docker compose up -d
```

## Key Production Features

- **Stateless API** — scale horizontally behind a load balancer
- **Persistent storage** — PostgreSQL for threads, checkpoints, and agent files
- **WebSocket streaming** — real-time agent step visibility
- **Rate limiting** — per-user/IP, configurable
- **JWT auth** — plug in OAuth2 (Google, GitHub) via the user ID
- **Structured logging** — JSON logs for log aggregation (DataDog, CloudWatch)
- **Health checks** — ready for Kubernetes / ECS auto-scaling
- **Multi-region ready** — deploy to US, EU, Asia for low-latency global access
