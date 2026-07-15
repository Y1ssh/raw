"""Agent endpoints (chat / stream / threads).

Sprint 0.5: ``POST /api/chat`` runs the durable graph for a ``thread_id`` and returns the final
state. The graph + Postgres checkpointer are built ONCE in the FastAPI lifespan (see main.py) and
stored on ``app.state`` — this handler just drives it.

The checkpointer is the SYNC ``PostgresSaver`` (DECISIONS D9), so ``graph.invoke`` is a blocking
call; we run it via ``run_in_threadpool`` so it never blocks the event loop. (The async pool upgrade
is deferred to Sprint 3.) Streaming (SSE) is also Sprint 3.
"""

from typing import Any

from fastapi import APIRouter, Request
from fastapi.concurrency import run_in_threadpool
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["agent"])


class ChatRequest(BaseModel):
    thread_id: str = Field(..., description="Durable conversation id — the checkpointer key.")
    message: str = Field(..., description="The user's message for this turn.")


class ChatResponse(BaseModel):
    thread_id: str
    state: dict[str, Any]


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request) -> ChatResponse:
    """Run the agent graph for one thread and return its final (durable) state."""
    graph: CompiledStateGraph[Any, Any, Any, Any] = request.app.state.graph
    config: RunnableConfig = {"configurable": {"thread_id": req.thread_id}}
    turn = {"messages": [{"role": "user", "content": req.message}]}

    def _invoke() -> dict[str, Any]:
        # sync PostgresSaver (D9) -> blocking call, kept off the event loop via run_in_threadpool
        result: dict[str, Any] = graph.invoke(turn, config)
        return result

    final = await run_in_threadpool(_invoke)
    return ChatResponse(thread_id=req.thread_id, state=final)
