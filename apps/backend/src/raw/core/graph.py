"""The LangGraph graph — State + Nodes + Edges, checkpointed to Postgres.

This wraps the pedagogical 30-line loop (core/loop.py) into a production execution engine: durable
state, resumability after a crash, and a hard iteration cap. The loop SHAPE is unchanged
(reason -> act -> observe); we add the machinery around it.

Domain-clean (BASE-VS-PACK.md):
  - ``agent`` is the only node that touches the LLM, and the model function is INJECTED
    (``call_model``) — the base ships no concrete adapter (that's the Sprint 1 llm slot).
  - ``tools`` is a documented NO-OP placeholder — a pack replaces it with a real MCP-backed node.
  - every routing decision is STRUCTURAL (in ``should_continue``), never a prompt instruction
    (design law #6).

The graph is returned UNCOMPILED so the caller supplies the checkpointer:
``build_graph(call_model).compile(checkpointer=PostgresSaver.from_conn_string(...))``. That
checkpointer is what makes state resumable (State + Memory rows of the base contract).
"""

from typing import Any

from langgraph.graph import END, START, StateGraph

from raw.core.loop import ModelFn
from raw.core.state import AgentState, Message


def build_graph(
    call_model: ModelFn, max_iterations: int = 10
) -> StateGraph[AgentState, Any, Any, Any]:
    """Build the durable ReAct graph around an injected ``call_model``.

    Args:
        call_model: the llm slot — ``list[dict] -> dict`` (a fake in tests, LiteLLM when deployed).
        max_iterations: hard cap on agent steps (the #1 guardrail) and on error retries.

    Returns:
        an uncompiled ``StateGraph``; call ``.compile(checkpointer=...)`` to run it.
    """

    def agent(state: AgentState) -> dict[str, Any]:
        """REASON: call the model on the transcript. Emits a +1 iteration delta.

        On success we also clear ``error_reason`` (a good step wipes any prior failure). On an
        exception we contain it: record the reason and route to ``error_handler`` instead of
        crashing the whole graph (guardrails — contain the blast radius).
        """
        try:
            response = call_model(state.messages)
        except Exception as exc:  # noqa: BLE001 — deliberately contain any model failure
            return {"iteration": 1, "error_reason": f"{type(exc).__name__}: {exc}"}
        return {"messages": [response], "iteration": 1, "error_reason": None}

    def tools(state: AgentState) -> dict[str, Any]:
        """ACT + OBSERVE: no-op placeholder. A pack swaps this for a real MCP-backed ToolNode.

        It consumes the last assistant message's ``tool_calls`` and emits one empty observation per
        call so the transcript stays well-formed — but executes nothing (the base has no tools).
        """
        last = state.messages[-1] if state.messages else {}
        calls = last.get("tool_calls") or []
        observations: list[Message] = [
            {"role": "tool", "tool_call_id": call.get("id"), "content": ""} for call in calls
        ]
        return {"messages": observations, "tool_results": observations}

    def error_handler(state: AgentState) -> dict[str, Any]:
        """Contain a failed agent step: bump the bounded retry counter (+1 delta)."""
        return {"retry_count": 1}

    def should_continue(state: AgentState) -> str:
        """Structural router after ``agent`` — NOT a prompt decision (design law #6).

        Order matters: an error routes to recovery; the iteration cap is terminal and beats any
        pending tool calls (so a runaway loop always stops); otherwise pending tool_calls -> tools,
        and a clean answer -> end.
        """
        if state.error_reason is not None:
            return "error_handler"
        if state.iteration >= max_iterations:
            return "end"
        last = state.messages[-1] if state.messages else {}
        if last.get("tool_calls"):
            return "tools"
        return "end"

    def should_retry(state: AgentState) -> str:
        """After ``error_handler``: retry the agent while under the cap, else give up cleanly."""
        return "agent" if state.retry_count < max_iterations else "end"

    graph: StateGraph[AgentState, Any, Any, Any] = StateGraph(AgentState)
    graph.add_node("agent", agent)
    graph.add_node("tools", tools)
    graph.add_node("error_handler", error_handler)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "error_handler": "error_handler", "end": END},
    )
    graph.add_edge("tools", "agent")
    graph.add_conditional_edges("error_handler", should_retry, {"agent": "agent", "end": END})
    return graph
