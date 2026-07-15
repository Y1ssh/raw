"""Typed agent state (Pydantic). ~60% of production incidents trace to state — get this right.

TODO (Sprint 0.5): reducers for concurrent updates; plan/tool_results/error fields.
"""

from typing import Any

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    messages: list[dict[str, Any]] = Field(default_factory=list)
    iteration: int = 0
