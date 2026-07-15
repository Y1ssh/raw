# Raw — DECISIONS log (why we chose what we chose)

> **How to use this doc:** every non-trivial decision is recorded here with its RATIONALE, so nobody
> (captain, architect, or Claude Code) has to re-derive or re-litigate it later. **Claude Code appends
> a new entry whenever it makes a decision.** Format: what · why · date · status (active / superseded).
> Newest at the bottom. Grounded in the 15-phase research + the GRAND SYNTHESIS + BASE-BUILD-PLAN docs.

---

### D1 — Build a domain-agnostic BASE, customized per project via PACKs
**Decision:** One reusable base (the "harness/chassis"), built once. Each project = a capability PACK
(tools + skills + prompt + rules + theme + validator) dropped onto the base. Same base + different
pack = different agent.
**Why:** Validated 3 ways — empirically (Cursor/Claude Code/Perplexity are all a model in the same
9-component harness), practically (production war stories: "architecture beats prompt; 80% engineering"),
canonically (12-Factor Agents). Build the hard part once → each new agent is days, not months.
**Status:** active.

### D2 — Base name = "Raw"
**Decision:** the base is named **Raw**. The research agent (pack #1) stays **Grounded**.
**Why:** descriptive ("an agent before it has skills"), positive, memorable, TBI-friendly, and reads
as "Raw + research pack = Grounded." Renameable via `gh repo rename` if ever needed.
**Status:** active.

### D3 — The base is MOAT-AGNOSTIC (the moat lives in the pack)
**Decision:** the base contains the eval MACHINERY but ZERO validators. The moat (e.g. RAGAS
faithfulness/source_recall) is a pack's `validator`.
**Why:** lets us build the base without a moat and add the moat per project. Keeps the base domain-clean
and reusable for any domain (research/time-series/coding).
**Status:** active.

### D4 — Build approach = HYBRID (reuse libraries + templates as wiring reference)
**Decision:** use standard LIBRARIES (langgraph, litellm, celery, langfuse, assistant-ui…) and reference
`wassim249/fastapi-langgraph-...` (chassis) + `vstorm-co/fastapi-fullstack` (pack/cockpit) for WIRING
patterns only. Build only the glue + base↔pack contract + packs + eval moat (the ~20% that's ours).
**Why:** Phase 14 — "reuse all infra/plumbing; never build models/orchestration/vectorDB/chat-UI/
observability (solved)." Forking a heavy template wholesale means gutting baggage; from-scratch rebuilds
solved plumbing. Hybrid is the middle path the research prescribes. For a portfolio it also shows the
skill (the arrangement) while reusing the industry-standard parts.
**Status:** active.

### D5 — Strategy = base-THROUGH-pack (build Grounded first, base emerges)
**Decision:** build one excellent agent (Grounded) ON the base+pack shape, rather than building an
abstract platform first. The base emerges as a byproduct.
**Why:** resolves the tension between the platform vision and the research's #1 law ("start narrow").
Avoids the 77% "platform-first" failure mode (Phase 13). The folder boundary (`packs/…`) makes the base
real without speculative platform-building.
**Status:** active.

### D6 — Orchestration = LangGraph (+ Postgres checkpointer)
**Decision:** LangGraph is the execution engine; state is externalized via a Postgres checkpointer.
**Why:** Phase 1 — the "safest serious production default"; State+Nodes+Edges + checkpoint-every-
transition; externalized state → resumable → horizontally scalable by design. (~60% of prod incidents
trace to state — so we get it typed + reduced.)
**Status:** active.

### D7 — Model gateway = LiteLLM, dependencies pinned via floors + committed uv.lock
**Decision:** LiteLLM as the model gateway. In `pyproject.toml` use sensible FLOORS (`>=`); the exact
reproducible pins live in the committed `uv.lock`. `litellm` floor is `>=1.84.0`.
**Why:** LiteLLM = the vendor-neutral swap seam (Phase 2.2). The floor `>=1.84.0` is deliberately ABOVE
the March-2026 compromised `1.82.7`/`1.82.8` (a credential-stealer, later yanked). Floors + lockfile is
standard modern practice and avoids pinning a single (possibly nonexistent or compromised) release.
**Lesson:** we once pinned the exact malicious `1.82.7` from memory — never guess versions; verify.
**Status:** active.

### D8 — Message representation = plain OpenAI-style dicts (not LangChain objects)
**Decision:** agent state carries messages as plain dicts (`{"role": ..., "content": ...}`), end to end.
**Why:** our gateway is LiteLLM, which uses OpenAI-style dicts; `core/loop.py` already uses dicts.
LangChain message objects would COUPLE the base to LangChain — against our provider-agnostic thesis.
**Implementation note:** `add_messages` (LangChain's reducer) may coerce dicts into message objects; if
so, use a small dict-safe append reducer (append + de-dup by id) so `state.messages` stays `list[dict]`.
**Status:** active.

### D9 — Checkpointer = SYNC PostgresSaver now; async pool DEFERRED to Sprint 3
**Decision:** Sprint 0.5 uses the sync `PostgresSaver`, driven off the event loop with
`run_in_threadpool`. The `AsyncPostgresSaver` + connection pool upgrade is deferred to Sprint 3 (scale).
**Why:** `run_in_threadpool` runs the sync DB call in a thread → it does NOT block the event loop (a
valid production pattern). Async pool is an optimization for high concurrency, which belongs in the scale
sprint (S3) alongside the queue — not the core sprint. Principle: start simple, add when needed. This is
sequencing, not a corner cut. Switching sync→async later is a localized change.
**Status:** active (revisit at S3).

### D10 — Postgres tests use testcontainers (hermetic), skip if Docker absent
**Decision:** the Postgres-backed tests (persist, resume) spin up an ephemeral Postgres via
`testcontainers[postgres]` (dev dep), and `pytest.skip()` if Docker is unavailable.
**Why:** hermetic integration testing is the industry standard — a real, isolated DB, torn down after,
no shared state. The skip-guard keeps pytest green everywhere. Docker is available in the dev WSL2 + CI,
so these tests actually run (not just skip).
**Status:** active.

### D11 — Structure = monorepo
**Decision:** one repo: `apps/backend` + `apps/frontend` + `example-pack`, with the pack loader/contract
in the backend.
**Why:** simplest for a base; one place for the whole chassis. Real packs (Grounded etc.) live in their
OWN repos later (the marketplace model, Phase 6).
**Status:** active.

### D12 — Planning tool = Lavish; First Mate deferred
**Decision:** use Kun Chen's **Lavish** (`kunchenguid/lavish-axi`) as a skill for visual HTML plans
(installed, not forked). Defer **First Mate** (parallel-agent orchestrator).
**Why:** Lavish gives visual plans with diagrams + annotations — exactly what we want, and it auto-themes
to the project. Forking is premature (reuse principle). First Mate is for running many parallel agents —
overkill for a solo base build; add later if needed.
**Status:** active.

### D13 — What is DEFERRED and to where (so we don't forget)
- Streaming (SSE) → **S3**
- Async checkpointer/pool → **S3** (see D9)
- Real tools / MCP servers → **packs** (base `tools` node stays a no-op placeholder)
- Concrete LLM adapter (real `call_model`) → **S1** (the llm slot)
- Validators / the moat → **packs** (base has eval machinery only, see D3)
- Themes / prompts / rules → **packs**
**Status:** active.
