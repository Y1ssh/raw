"""Sprint 0.5 gate — 4 proofs the durable ReAct core actually works.

  1. reason -> act -> observe runs (agent -> tools -> agent)         [MemorySaver]
  2. state persists to Postgres across a fresh graph instance         [PostgresSaver]
  3. run resumes after an interruption on a fresh graph               [PostgresSaver]
  4. the iteration cap stops an infinite loop                         [MemorySaver]

Proofs 2 & 3 need a real Postgres. Per DECISIONS D10 we spin one up hermetically with
``testcontainers[postgres]`` and ``pytest.skip`` if Docker (or the package) is unavailable — so the
suite stays green everywhere, and actually runs where Docker exists (dev WSL2 + CI).
"""

from collections.abc import Iterator
from typing import Any

import pytest
from langgraph.checkpoint.memory import MemorySaver

from raw.core.graph import build_graph
from raw.core.state import Message

# --- stateless fake models (functions of the transcript, so they survive resume) ---------------


def call_done(messages: list[Message]) -> Message:
    """Finishes immediately — no tool calls."""
    return {"role": "assistant", "content": "hi", "tool_calls": None}


def call_react(messages: list[Message]) -> Message:
    """One tool call, then done — keyed off the transcript, not a hidden counter.

    Stateless on purpose: proof 3 resumes on a brand-new graph object, so behaviour must derive
    only from the (persisted) messages, never from closure state.
    """
    if any(m.get("role") == "tool" for m in messages):
        return {"role": "assistant", "content": "done", "tool_calls": None}
    return {"role": "assistant", "content": "", "tool_calls": [{"id": "c1", "name": "noop"}]}


def call_always_tool(messages: list[Message]) -> Message:
    """Never stops on its own — only the iteration cap can end it."""
    return {"role": "assistant", "content": "", "tool_calls": [{"id": "loop", "name": "noop"}]}


# --- proof 1: reason -> act -> observe -----------------------------------------------------------


def test_reason_act_observe_cycle() -> None:
    graph = build_graph(call_react).compile(checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "react-1"}}

    final = graph.invoke({"messages": [{"role": "user", "content": "go"}]}, cfg)

    assert final["iteration"] == 2, "agent should run twice (before and after the tool)"
    assert any(m.get("role") == "tool" for m in final["messages"]), "observation missing"
    assert final["messages"][-1]["content"] == "done", "did not finish after observing"
    assert final["tool_results"], "tool_results should record the observation"


# --- proof 4: the iteration cap holds ------------------------------------------------------------


def test_iteration_cap_stops_infinite_loop() -> None:
    graph = build_graph(call_always_tool, max_iterations=5).compile(checkpointer=MemorySaver())
    cfg = {"configurable": {"thread_id": "cap-1"}}

    final = graph.invoke({"messages": [{"role": "user", "content": "loop"}]}, cfg)

    assert final["iteration"] == 5, "the cap must stop the loop exactly at max_iterations"


# --- Postgres-backed proofs (hermetic testcontainer, skip if Docker absent) ----------------------


@pytest.fixture(scope="module")
def postgres_url() -> Iterator[str]:
    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:  # pragma: no cover - env without the dev dep
        pytest.skip("testcontainers[postgres] not installed")

    try:
        container = PostgresContainer("postgres:16-alpine", driver=None)
        container.start()
    except Exception as exc:  # pragma: no cover - env without a Docker daemon
        pytest.skip(f"Docker unavailable for testcontainers: {exc}")

    try:
        yield container.get_connection_url()
    finally:
        container.stop()


# --- proof 2: state persists to Postgres ---------------------------------------------------------


def test_state_persists_to_postgres(postgres_url: str) -> None:
    from langgraph.checkpoint.postgres import PostgresSaver

    cfg: dict[str, Any] = {"configurable": {"thread_id": "persist-1"}}

    with PostgresSaver.from_conn_string(postgres_url) as checkpointer:
        checkpointer.setup()
        graph = build_graph(call_done).compile(checkpointer=checkpointer)
        graph.invoke({"messages": [{"role": "user", "content": "remember me"}]}, cfg)

    # A completely fresh graph + connection over the SAME database must see the saved state.
    with PostgresSaver.from_conn_string(postgres_url) as checkpointer2:
        graph2 = build_graph(call_done).compile(checkpointer=checkpointer2)
        snapshot = graph2.get_state(cfg)

    assert snapshot.values["iteration"] == 1
    assert any(m["content"] == "remember me" for m in snapshot.values["messages"])


# --- proof 3: resume after interruption ----------------------------------------------------------


def test_resume_after_interruption(postgres_url: str) -> None:
    from langgraph.checkpoint.postgres import PostgresSaver

    cfg: dict[str, Any] = {"configurable": {"thread_id": "resume-1"}}

    # First worker: interrupt before the tools node — the run pauses mid-flight.
    with PostgresSaver.from_conn_string(postgres_url) as checkpointer:
        checkpointer.setup()
        graph = build_graph(call_react).compile(
            checkpointer=checkpointer, interrupt_before=["tools"]
        )
        graph.invoke({"messages": [{"role": "user", "content": "go"}]}, cfg)
        paused = graph.get_state(cfg)
        assert paused.next == ("tools",), "should be paused right before the tools node"

    # Second worker (fresh graph + connection): resume from the checkpoint and finish.
    with PostgresSaver.from_conn_string(postgres_url) as checkpointer2:
        graph2 = build_graph(call_react).compile(
            checkpointer=checkpointer2, interrupt_before=["tools"]
        )
        final = graph2.invoke(None, cfg)  # None input = resume from where it stopped
        done = graph2.get_state(cfg)

    assert done.next == (), "the resumed run should reach the end"
    assert final["iteration"] == 2
    assert final["messages"][-1]["content"] == "done"
