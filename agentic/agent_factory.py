from __future__ import annotations

import importlib
from typing import Literal

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StateBackend, StoreBackend
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import MemorySaver
from tavily import TavilyClient
from pydantic import BaseModel, Field

from agentic.config import settings


def _has_postgres() -> bool:
    return importlib.util.find_spec("psycopg") is not None


class ResearchFindings(BaseModel):
    summary: str = Field(description="Summary of findings")
    confidence: float = Field(description="Confidence score from 0 to 1")
    sources: list[str] = Field(description="List of source URLs")


_tavily_client: TavilyClient | None = None


def get_tavily_client() -> TavilyClient | None:
    global _tavily_client
    if not settings.tavily_api_key:
        return None
    if _tavily_client is None:
        _tavily_client = TavilyClient(api_key=settings.tavily_api_key)
    return _tavily_client


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search using Tavily."""
    client = get_tavily_client()
    if not client:
        return {"error": "Tavily API key not configured"}
    return client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


DEFAULT_SYSTEM_PROMPT = (
    "You are an expert AI assistant and researcher. "
    "You conduct thorough research using your internet_search tool when needed, "
    "plan multi-step work with write_todos, offload bulky content to files, "
    "and always cite sources when research was involved."
)


async def build_agent(
    user_id: str = "anonymous",
    model: str | None = None,
):
    model = model or settings.default_model

    common_tools = []
    if settings.tavily_api_key:
        common_tools.append(internet_search)

    subagents = [
        {
            "name": "research-agent",
            "description": "Used to research more in depth questions",
            "system_prompt": (
                "You are a great researcher. Research thoroughly and cite your sources."
            ),
            "tools": common_tools,
        },
        {
            "name": "structured-researcher",
            "description": "Researches topics and returns structured findings",
            "system_prompt": "Research the given topic thoroughly. Return your findings.",
            "tools": common_tools,
            "response_format": ResearchFindings,
        },
    ]

    if _has_postgres() and settings.database_url.startswith("postgresql") and settings.app_env != "development":
        try:
            from psycopg_pool import AsyncConnectionPool
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            from langgraph.store.postgres.aio import AsyncPostgresStore

            pool = AsyncConnectionPool(
                conninfo=settings.database_url.replace("+psycopg", ""),
                max_size=10,
            )
            checkpointer = AsyncPostgresSaver(pool)
            store = AsyncPostgresStore(pool)
            backend = StoreBackend(
                store=store,
                namespace=lambda rt: ("users", user_id),
            )
        except Exception:
            checkpointer = MemorySaver()
            store = InMemoryStore()
            backend = StateBackend()
    else:
        checkpointer = MemorySaver()
        store = InMemoryStore()
        backend = StateBackend()

    agent = create_deep_agent(
        model=model,
        tools=common_tools,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        subagents=subagents,
        backend=backend,
        checkpointer=checkpointer,
        store=store,
    )

    return agent
