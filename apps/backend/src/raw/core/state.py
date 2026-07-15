"""Typed agent state (Pydantic). ~60% of production incidents trace to state — get this right.

Every field carries a REDUCER (via ``Annotated``) so that when several nodes write the same key
in one LangGraph super-step, the writes MERGE deterministically instead of racing (a bare
concurrent write to an un-reduced key raises "InvalidUpdateError: concurrent write, no reducer").
Nodes return partial deltas (e.g. ``{"iteration": 1}``); LangGraph folds each delta into the
running value with that field's reducer.

Design law (see docs/DECISIONS.md D8): messages stay plain OpenAI-style ``dict`` end-to-end so the
base is provider-agnostic (matches LiteLLM + core/loop.py). We therefore DO NOT use LangChain's
``add_messages`` (it coerces dicts into LangChain message objects) — ``append_messages`` below is a
small dict-safe replacement.
"""

import operator
from typing import Annotated, Any

from pydantic import BaseModel, Field

Message = dict[str, Any]


def append_messages(left: list[Message], right: list[Message]) -> list[Message]:
    """Dict-safe append reducer — the replacement for LangChain's ``add_messages`` (D8).

    Appends ``right`` onto ``left`` while keeping every element a plain ``dict``. Messages carrying
    an ``id`` are de-duped: a later message with a known id REPLACES the earlier one in place (so a
    node can revise a message), rather than appending a duplicate. Messages without an ``id`` are
    always appended.
    """
    merged: list[Message] = list(left)
    index_by_id: dict[Any, int] = {
        m["id"]: i for i, m in enumerate(merged) if isinstance(m, dict) and "id" in m
    }
    for msg in right:
        mid = msg.get("id") if isinstance(msg, dict) else None
        if mid is not None and mid in index_by_id:
            merged[index_by_id[mid]] = msg
        else:
            if mid is not None:
                index_by_id[mid] = len(merged)
            merged.append(msg)
    return merged


def take_last[T](left: T, right: T) -> T:
    """Last-write-wins reducer for scalar fields (``plan``, ``error_reason``).

    Its job is to make concurrent writes to a scalar LEGAL (avoids the "no reducer" crash) and to
    let a node CLEAR a value by writing ``None`` — the agent node clears ``error_reason`` on a
    successful step this way, so a stale error can't re-trigger the error path on the next turn.
    """
    return right


class AgentState(BaseModel):
    """The durable, checkpointed state of one agent thread.

    Domain-clean: no tool schemas, prompts, or validators live here — those come from packs. This is
    just the machinery every agent needs (BASE-VS-PACK.md rows Loop + State + Guardrails).
    """

    # Conversation transcript — plain dicts, appended & de-duped by id (never LangChain objects).
    messages: Annotated[list[Message], append_messages] = Field(default_factory=list)
    # Super-step counter — nodes emit +1 deltas that operator.add sums (never lost on a race).
    iteration: Annotated[int, operator.add] = 0
    # Observations from the tools node — concurrent tool runs concatenate, none dropped.
    tool_results: Annotated[list[Message], operator.add] = Field(default_factory=list)
    # Bounded retry accounting for the error_handler — delta-based, same shape as iteration.
    retry_count: Annotated[int, operator.add] = 0
    # Optional plan text (a planner pack may set it) — last write wins.
    plan: Annotated[str | None, take_last] = None
    # Why the last agent step failed; set by error_handler, cleared by a good agent step.
    error_reason: Annotated[str | None, take_last] = None
