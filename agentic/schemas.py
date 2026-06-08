from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=100_000)
    thread_id: str | None = None
    model: str | None = None
    stream: bool = True


class ChatResponse(BaseModel):
    thread_id: str
    message: str
    files: dict = {}


class AgentStep(BaseModel):
    type: Literal[
        "plan",
        "tool_call",
        "tool_result",
        "subagent_start",
        "subagent_end",
        "text",
        "error",
    ]
    content: str
    metadata: dict = {}


class ThreadSummary(BaseModel):
    thread_id: str
    user_id: str
    created_at: datetime
    message_count: int
    last_message: str


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
