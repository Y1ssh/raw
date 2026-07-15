"""Raw backend entrypoint. FastAPI app wiring the base together.

Sprint 0: health + config load (fail fast).
Sprint 0.5: the durable ReAct graph + Postgres checkpointer are built ONCE in the lifespan and
stored on ``app.state`` so ``POST /api/chat`` can drive them (externalized state -> resumable).
Later sprints add streaming, the queue, and observability. Run: ``make dev``.
"""

import logging
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from langgraph.checkpoint.postgres import PostgresSaver

from raw import __version__
from raw.api import health, routes
from raw.config import Settings, get_settings
from raw.core.graph import build_graph
from raw.core.state import Message


def _placeholder_model(messages: list[Message]) -> Message:
    """The base's no-op ``call_model`` — a stand-in for the Sprint 1 llm slot (DECISIONS D13).

    The base ships NO concrete LLM adapter (that would be domain-ish and belongs in the llm slot /
    a pack). This placeholder just closes the loop so the graph is runnable end-to-end: it returns a
    tool-less assistant message, so the agent reasons exactly once and stops. A real deploy injects
    a LiteLLM-backed ``call_model`` here instead.
    """
    return {"role": "assistant", "content": "", "tool_calls": None}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Build the graph + checkpointer on startup; tear the checkpointer down gracefully on shutdown.

    Golden rule #6: never hard-kill a process holding the checkpointer/DB open — we exit the
    ``PostgresSaver`` context manager cleanly so its connection is released.
    """
    settings: Settings = get_settings()
    call_model: Callable[[list[Message]], Message] = _placeholder_model
    with PostgresSaver.from_conn_string(settings.postgres_url) as checkpointer:
        checkpointer.setup()  # idempotent: create the checkpoint tables if absent
        app.state.graph = build_graph(call_model, settings.max_iterations).compile(
            checkpointer=checkpointer
        )
        logging.getLogger("raw").info("graph compiled with Postgres checkpointer")
        yield
    # context exit released the checkpointer connection — graceful shutdown complete.


def create_app() -> FastAPI:
    settings = get_settings()  # validates config on startup — fail fast
    logging.basicConfig(level=settings.log_level)
    app: FastAPI = FastAPI(title="Raw", version=__version__, lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(routes.router)
    return app


app = create_app()


__all__ = ["app", "create_app", "lifespan"]
