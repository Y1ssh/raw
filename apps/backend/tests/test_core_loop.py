"""The 30-line core is the heart of the base — test it directly."""

from typing import Any

from raw.core.loop import run_agent_loop


def test_loop_stops_when_no_tool_calls() -> None:
    def call_model(_messages: list[dict[str, Any]]) -> dict[str, Any]:
        return {"role": "assistant", "content": "done", "tool_calls": None}

    def execute_tools(_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return []

    result = run_agent_loop([], call_model, execute_tools)
    assert result["content"] == "done"


def test_loop_respects_iteration_cap() -> None:
    calls = {"n": 0}

    def call_model(_messages: list[dict[str, Any]]) -> dict[str, Any]:
        calls["n"] += 1
        return {"role": "assistant", "tool_calls": [{"name": "noop"}]}  # never finishes

    def execute_tools(_calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{"role": "tool", "content": "ok"}]

    run_agent_loop([], call_model, execute_tools, max_iterations=3)
    assert calls["n"] == 3  # capped — no infinite loop
