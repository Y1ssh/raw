# Raw — ROADMAP & progress (the grand checklist)

> **How to use this doc:** this is the single source of truth for what we're building and how far we
> are. **Claude Code updates the Status column as tasks complete.** Legend: ☐ todo · 🔄 in progress ·
> ✅ done · ⏭️ deferred (to a later sprint). Each sprint has a GATE = the "prove it works" bar; do not
> mark a sprint done until its gate passes (`pytest` + `ruff` + `mypy --strict`).

## Status at a glance
| Sprint | What | Status | Gate met? |
|---|---|---|---|
| S0 | Scaffold + hygiene + CI + config + 30-line core + pack seam | ✅ done | ✅ (tests pass, pushed) |
| S0.5 | The core — LangGraph graph + typed state + Postgres checkpointer + /api/chat | 🔄 in progress | ☐ |
| S1 | The slots — LLM gateway, tools/MCP, context, guardrails, memory, vector | ☐ todo | ☐ |
| S2 | The seam — flesh out pack loader + contract + example pack | ☐ todo | ☐ |
| S3 | The surface + scale — streaming, queue, rate-limit, frontend shell, **async checkpointer** | ☐ todo | ☐ |
| S4 | Production — observability, eval machinery, guardrail rails, cost controls, deploy | ☐ todo | ☐ |

---

## S0 — Scaffold + hygiene ✅ DONE
- ✅ Repo hygiene (README, LICENSE, .gitignore, .env.example, CONTRIBUTING, SECURITY, CHANGELOG, Makefile)
- ✅ CI (GitHub Actions) + Dependabot + PR/issue templates
- ✅ docker-compose (postgres + redis) + multi-stage Dockerfile
- ✅ docs: ARCHITECTURE, BASE-VS-PACK, HOW-TO-BUILD-A-PACK, DEPLOYMENT
- ✅ config system (pydantic-settings, the slot selector)
- ✅ the 30-line core loop (`core/loop.py`) + passing tests
- ✅ pack loader + contract (the seam) + example-pack smoke test
- ✅ pushed to github.com/Y1ssh/raw
**GATE ✅:** repo exists, CI wired, tests pass.

## S0.5 — The core (Durable ReAct engine) 🔄 IN PROGRESS
Wrap the 30-line loop in a LangGraph graph with durable, resumable, capped state. **Domain-clean.**
- ☐ `core/state.py` — typed `AgentState` (Pydantic) + concurrency-safe reducers (messages [dict-safe], iteration, retry_count, tool_results, plan, error_reason)
- ☐ `core/graph.py` — nodes (agent = reason/LLM slot, tools = no-op placeholder, error_handler) + `should_continue` structural router + iteration cap + PostgresSaver checkpointer
- ☐ `api/routes.py` — `POST /api/chat` runs the graph for a thread_id, returns final state (build graph in FastAPI **lifespan**; wire lifespan into `main.py`)
- ☐ `tests/test_graph.py` — 4 proofs: (1) reason→act→observe cycle, (2) state persists to Postgres, (3) resume after interruption, (4) iteration cap stops loops
- ☐ add + pin `testcontainers[postgres]` (dev), run `uv lock`
**GATE:** bare agent runs Reason→Act→Observe on LangGraph · state persists to Postgres · resumes after restart · iteration cap holds · pytest/ruff/mypy --strict pass.

## S1 — The slots (swappable layers)
- ☐ LLM gateway slot — LiteLLM wrapper (routing, fallback); this is the concrete `call_model` the graph injects
- ☐ Tool registry slot — MCP client + registration + routing + progressive loading (bounded-sticky)
- ☐ Context manager — write/select/compress/isolate + compaction (keep task/IDs verbatim; <40% fill)
- ☐ Guardrails machinery — input/output rail interfaces (validators come from packs)
- ☐ Memory slot — long-term interface (mem0/LangMem) alongside the checkpointer
- ☐ Vector slot — interface + pgvector adapter + qdrant adapter (RAG strategy is a pack's, not the base's)
**GATE:** swap model/DB via config (no code change) · tools register + run · context compacts.

## S2 — The seam (pack loader)
- ☐ Flesh out `packs/loader.py` — register a pack's tools/skills/prompt/rules/theme/validator, namespaced
- ☐ Enforce the contract (namespacing, `${PACK_ROOT}`/`${PACK_DATA}`, isolation)
- ☐ Prove with the example-pack (its placeholder tool wires into the base)
**GATE:** drop in a pack → its components register + run. The base+pack split is real end to end.

## S3 — The surface + scale
- ☐ FastAPI streaming (SSE) — reasoning + tool cards + answer
- ☐ Celery + Redis queue — long agent jobs off the request path (agent = a job)
- ☐ Rate limiting (slowapi) + per-tenant quotas
- ☐ Frontend shell — assistant-ui (chat + canvas + autonomy slider + threads), unskinned
- ☐ **Upgrade checkpointer sync → AsyncPostgresSaver + pool** (deferred here from S0.5 — see DECISIONS #9)
**GATE:** end-to-end via the UI · long jobs queue · streaming works.

## S4 — Production-ready
- ☐ Observability — Langfuse (self-host) + OpenLLMetry (OTel), full-session traces
- ☐ Eval machinery — the harness that RUNS a pack's validator (no validator baked in)
- ☐ Guardrail rails — input/retrieval/output/execution (LLM Guard + NeMo)
- ☐ Cost controls — model routing (70/20/10), prefix caching, budgets, circuit breakers
- ☐ Deployment — Docker → Dokploy (self-host) / K8s; security regression tests in CI
**GATE:** traces visible · a pack's validator runs via the machinery · deployable · budgets + circuit breakers.

---

## After the base: packs (separate repos)
- ☐ **Grounded** = Raw + research pack (RAG + RAGAS validator) — the first agent, the moat proof
- ☐ Agent #2 (e.g. time-series) — only if proven; validates the base is domain-agnostic
