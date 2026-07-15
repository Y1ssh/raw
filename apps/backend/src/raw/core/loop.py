"""The 30-line core loop.

Understand THIS before reaching for LangGraph. Every agent framework (Claude Code, Cursor,
Codex, LangGraph, smolagents) is this same reason->act->observe loop "in different costumes."
graph.py (Sprint 0.5) wraps it with durable state, resumability, and observability — but the
shape underneath is exactly this.
"""

from collections.abc import Callable
from typing import Any

ModelFn = Callable[[list[dict[str, Any]]], dict[str, Any]]
ToolExecutor = Callable[[list[dict[str, Any]]], list[dict[str, Any]]]


def run_agent_loop(
    messages: list[dict[str, Any]],
    call_model: ModelFn,
    execute_tools: ToolExecutor,
    max_iterations: int = 10,
) -> dict[str, Any]:
    """The universal agent loop. A deterministic shell around a stochastic core."""
    response: dict[str, Any] = {}
    for _ in range(max_iterations):  # iteration cap = the #1 guardrail
        response = call_model(messages)  # REASON
        tool_calls = response.get("tool_calls")
        if not tool_calls:  # no tool calls -> done
            return response
        observations = execute_tools(tool_calls)  # ACT
        messages.append(response)
        messages.extend(observations)  # OBSERVE
    return response  # hit the cap -> return last response (never loop forever)
