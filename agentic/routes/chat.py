from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from langchain_core.messages import HumanMessage

from agentic.auth import get_current_user
from agentic.rate_limit import check_rate_limit
from agentic.schemas import ChatRequest, AgentStep
from agentic.agent_factory import build_agent

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat")
async def chat(
    body: ChatRequest,
    user_id: str = Depends(get_current_user),
    _=Depends(check_rate_limit),
):
    """Start or continue a conversation. Returns the agent's final answer."""
    thread_id = body.thread_id or str(uuid.uuid4())
    agent = await build_agent(user_id=user_id, model=body.model)

    result = await agent.ainvoke(
        {"messages": [HumanMessage(content=body.message)]},
        config={"configurable": {"thread_id": thread_id}, "recursion_limit": 100},
    )

    return {
        "thread_id": thread_id,
        "message": result["messages"][-1].content,
        "files": result.get("files", {}),
    }


@router.websocket("/ws/{thread_id}")
async def chat_websocket(
    websocket: WebSocket,
    thread_id: str,
):
    """Stream agent execution step-by-step over WebSocket."""
    await websocket.accept()

    user_id = "anonymous"
    model = None

    try:
        data = await websocket.receive_json()
        message = data.get("message", "")
        user_id = data.get("user_id", "anonymous")
        model = data.get("model", None)
    except Exception:
        await websocket.close(code=1003)
        return

    if not message:
        await websocket.send_json(
            AgentStep(type="error", content="Message is required").model_dump()
        )
        await websocket.close()
        return

    agent = await build_agent(user_id=user_id, model=model)

    try:
        async for event in agent.astream_events(
            {"messages": [HumanMessage(content=message)]},
            config={
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 100,
            },
            version="v2",
        ):
            kind = event.get("event", "")
            name = event.get("name", "")

            if kind == "on_chat_model_start":
                await websocket.send_json(
                    AgentStep(type="plan", content="Thinking...").model_dump()
                )
            elif kind == "on_tool_start":
                tool_input = event.get("data", {}).get("input", {})
                await websocket.send_json(
                    AgentStep(
                        type="tool_call",
                        content=json.dumps(tool_input),
                        metadata={"tool": name},
                    ).model_dump()
                )
            elif kind == "on_tool_end":
                output = event.get("data", {}).get("output", "")
                preview = str(output)[:500]
                await websocket.send_json(
                    AgentStep(
                        type="tool_result",
                        content=preview,
                        metadata={"tool": name},
                    ).model_dump()
                )
            elif kind == "on_chain_end" and name == "LangGraph":
                output = event.get("data", {}).get("output", {})
                messages = output.get("messages", [])
                if messages:
                    final = messages[-1].content
                    await websocket.send_json(
                        AgentStep(type="text", content=str(final)).model_dump()
                    )

        await websocket.send_json(
            AgentStep(type="text", content="[DONE]").model_dump()
        )

    except WebSocketDisconnect:
        pass
    except Exception as exc:
        await websocket.send_json(
            AgentStep(type="error", content=str(exc)).model_dump()
        )
    finally:
        await websocket.close()
