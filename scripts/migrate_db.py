#!/usr/bin/env python3
"""Initialize the PostgreSQL database for LangGraph checkpointing and store."""

import asyncio
import os

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore
from psycopg_pool import AsyncConnectionPool


async def main():
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql://agentic:agentic@localhost:5432/agentic",
    )

    async with AsyncConnectionPool(
        conninfo=database_url,
        max_size=20,
    ) as pool:
        # Initialize checkpoint tables
        checkpointer = PostgresSaver(async_connection_pool=pool)
        await checkpointer.setup()

        # Initialize store tables
        store = PostgresStore(async_connection_pool=pool)
        await store.setup()

        print("Database migration complete.")
        print("  - LangGraph checkpointer tables created")
        print("  - LangGraph store tables created")


if __name__ == "__main__":
    asyncio.run(main())
