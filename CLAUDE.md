# CLAUDE.md — Raw operating manual (READ THIS FIRST, every session)

You are working on **Raw**, a domain-agnostic agent BASE (a reusable chassis). The docs below are the
source of truth. Read them before writing code, and **update them as you work** (see Workflow).

## What Raw is (in one breath)
A 12-factor stateless-reducer HARNESS. Give it a PACK (tools + skills + prompt + rules + theme +
validator) and it becomes a specific agent:
`Raw + research pack = Grounded` · `Raw + coding pack = a Cursor-like agent`.
**This repo is the BASE ONLY — no moat, no domain, no pack.**

## Read these FIRST (source of truth)
- `docs/BASE-VS-PACK.md` — THE CONTRACT: what is base vs pack. The most important doc.
- `docs/ARCHITECTURE.md` — the 9-component harness + the 7 design laws.
- `docs/ROADMAP.md` — the sprint plan + live progress table. **UPDATE status as you finish tasks.**
- `docs/DECISIONS.md` — every decision + WHY. **APPEND an entry whenever you make a decision.**

## Golden rules (non-negotiable)
1. **BASE vs PACK** — only add code COMMON to every agent. Domain-specific → a pack repo. Unsure? Read `docs/BASE-VS-PACK.md`.
2. **DOMAIN-CLEAN** — no tools/prompts/validators/themes in the base. The `tools` node stays a no-op placeholder.
3. **PROVIDER-AGNOSTIC** — messages are plain OpenAI-style dicts (matches LiteLLM + `core/loop.py`). Do NOT couple the base to LangChain message objects. If a reducer coerces dicts, use a dict-safe reducer instead.
4. **REUSE, don't rebuild** — use standard libraries (langgraph, litellm, celery, langfuse). Reference `wassim249/fastapi-langgraph-...` + `vstorm-co/fastapi-fullstack` for WIRING patterns only, never their domain code. Build only glue + contract + packs + moat.
5. **PIN dependencies** — floors in `pyproject.toml` + committed `uv.lock`. Never float `litellm` (the March-2026 1.82.7/1.82.8 supply-chain incident).
6. **GRACEFUL shutdown** — never hard-kill a process holding the checkpointer/DB open.
7. **Hard rules are STRUCTURAL** (in code), not prompt instructions.
8. **VERIFY before "done"** — `pytest` + `ruff check` + `mypy --strict` must pass. Report the output; don't claim done without it.
9. **Plan with Lavish** — for any non-trivial work, produce a visual Lavish plan first, get approval, then build.

## Workflow every session
1. Read the 4 docs above (BASE-VS-PACK, ARCHITECTURE, ROADMAP, DECISIONS).
2. Check `docs/ROADMAP.md` for the current sprint + open tasks.
3. Do the work (plan in Lavish for anything non-trivial).
4. **UPDATE `docs/ROADMAP.md`** (mark tasks/status) and **`docs/DECISIONS.md`** (any new decision + why).
5. Run the gates (pytest / ruff / mypy). Report the output.

## Current status
See `docs/ROADMAP.md`. (At seeding: Sprint 0 ✅ done & pushed; Sprint 0.5 in progress.)

## Who's who (so context is never lost)
- **The captain** = Yash (Y1ssh). Sets direction. Has a TBI memory profile → keep docs current; every session starts cold from these files.
- **The architect** = the planning assistant (chat). Holds the long-term plan; grounds every decision in the research docs.
- **You** = Claude Code, the builder. Read the docs, build, keep ROADMAP + DECISIONS updated so all three stay in sync.
