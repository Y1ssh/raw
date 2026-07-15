# Architecture

Raw is a **12-factor stateless-reducer harness** — the same 9-component harness every production
agent (Cursor, Claude Code, Perplexity) is built from. The base is the harness; a pack turns it
into a specific agent.

## The 9 harness components
```
 ① model-interface (LiteLLM)     ② tool-registry (MCP)
 ③ context-manager               ④ planning (ReAct/Plan)
 ⑤ execution-loop (LangGraph)    ⑥ memory (checkpointer + slot)
 ⑦ feedback-loop (observe)       ⑧ guardrails (contain)
 ⑨ orchestration (LangGraph)     + a surface shell (assistant-ui)
```

## Governing principles (12-factor agents)
1. The harness is the product, not the model.
2. Deterministic code + LLM at the right points.
3. Own your context window (never fill past ~40% — the "dumb zone").
4. Stateless + externalized state (resumable -> horizontally scalable).
5. Separate reasoning CORE from swappable CAPABILITIES (base + pack).
6. Enforce hard rules structurally, not in prompts.
7. Measure everything (eval-driven).

## Data flow (one turn)
```
 request -> API (async) -> [queue for long jobs] -> worker:
   assemble context -> LLM reasons + picks tool -> execute (sandboxed) ->
   observe -> checkpoint state (Postgres) -> repeat until done or iteration cap
 -> stream (SSE) reasoning + tool cards + answer to the UI
```

## Why stateless + externalized state
A crashed worker resumes from the last checkpoint on another worker. Add worker pods = handle more
load. The base is horizontally scalable BY DESIGN.

## Security posture
Prompt injection is treated as UNSOLVED -> contain the blast radius (least-privilege tools, sandbox,
HITL on risky actions, output validation). Secrets never enter prompts or logs.
