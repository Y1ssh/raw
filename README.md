# Raw 🥚 — a domain-agnostic agent base

**Raw is an agent with no skills yet.** It is the reusable *chassis* (the harness) that every
specialized agent is built from. Give Raw a **pack** (tools + skills + prompt + rules + theme +
validator) and it becomes a real agent:

```
  Raw + research pack   = Grounded  (RAG + RAGAS)
  Raw + time-series pack = a forecasting agent
  Raw + coding pack      = a Cursor-like coding agent
```

> **This repo contains ONLY the base.** No moat, no domain, no pack. Anything specific to a
> project lives in a separate pack repo. If you'd rebuild it per project, it does **not** belong here.

## What's in the base (the ~80% common to every agent)
- **The harness** — LangGraph loop, typed state + Postgres checkpointer, context engineering, guardrails
- **The slots** (swap via config, no code change) — LLM gateway (LiteLLM), memory, vector DB, tools (MCP)
- **The shell** — assistant-ui chat + canvas, streaming, autonomy slider, threads
- **Production** — queue + stateless workers, observability, cost controls, Docker, CI
- **The seam** — the pack loader + the pack contract (`docs/BASE-VS-PACK.md`)

## What's NOT in the base (the ~20%, per project, in a pack repo)
Tools · skills · system prompt · rules · theme · **the validator (= the moat)** · the RAG pipeline.

## Quickstart
```bash
cp .env.example .env         # fill in as needed
make up                      # start postgres + redis
make dev                     # run the backend (http://localhost:8077)
make test                    # run tests
make lint                    # ruff + mypy
```

## Architecture
See `docs/ARCHITECTURE.md`. The base is a **12-factor stateless-reducer harness** — the same
9-component harness every production agent (Cursor, Claude Code, Perplexity) is built from.

## Build a new agent (a pack)
See `docs/HOW-TO-BUILD-A-PACK.md`.

## License
MIT — see `LICENSE`.
