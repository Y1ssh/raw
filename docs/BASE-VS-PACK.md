# BASE vs PACK — the contract (read this first)

This is the single most important document in Raw. It defines the boundary: what the **base**
provides vs what a **pack** supplies. Everything else follows from it.

## The rule
> If it is COMMON to every agent → it's the **base** (this repo).
> If it is SPECIFIC to one project → it's a **pack** (a separate repo).
> If you'd rebuild it per project, it is NOT the base.

## The base provides (the machinery)
| Layer | Base gives you |
|---|---|
| Loop | the reason->act->observe execution loop (LangGraph) |
| State | typed state + reducers + Postgres checkpointer (resumable) |
| Context | write/select/compress/isolate + compaction (<40% fill) |
| LLM | a gateway slot (LiteLLM) — swap the model via config |
| Tools | MCP registry + routing + progressive loading + sandbox interface |
| Memory | checkpointer (short) + a long-term slot |
| Vector | a retrieval slot + pgvector/qdrant adapters (the RAG *strategy* is the pack's) |
| Guardrails | input/output rails interface + iteration caps + error-handler node |
| Eval | the machinery that RUNS a validator (no validator baked in) |
| UI | the shell (chat + canvas + streaming + autonomy slider + threads) |
| Scale | queue + stateless workers + externalized state |
| Deploy | Docker + config + CI |
| Seam | the pack loader + this contract |

## A pack supplies (the domain content) — the ~20%
| Component | What | Example (research) |
|---|---|---|
| manifest (`pack.json`) | name, version, what it provides | "research-pack" |
| tools | the actions (MCP servers / @tool) | search_corpus, cite |
| skills | workflows (SKILL.md) | PRISMA lit-review |
| system prompt | the persona | "cite everything, abstain if unsure" |
| rules | the limits | never fabricate citations |
| theme | the UI skin (tokens) | evidence panels, trust-blue |
| **validator (= the MOAT)** | the quality gate | RAGAS faithfulness + source_recall |
| config | which DB / model | pgvector, qwen2.5 |

## The pack contract (what a pack MUST implement)
A pack is a folder with a `pack.json` manifest and known subfolders. The base's loader
(`apps/backend/src/raw/packs/loader.py`) discovers it, reads the manifest, and registers its
components. See `apps/backend/src/raw/packs/contract.py` for the exact interface.

```
 my-pack/
 ├── pack.json          # manifest (name, version, provides)
 ├── tools/             # MCP servers / @tool files
 ├── skills/            # SKILL.md workflows
 ├── prompt.md          # the system prompt
 ├── rules.md           # the limits
 ├── theme/tokens.json  # the UI skin
 └── validator.py       # the moat (quality gate)
```

**Conventions:**
- **Namespacing:** components are namespaced `pack-name:component` so packs never collide.
- **`${PACK_ROOT}`** = immutable installed files. **`${PACK_DATA}`** = persistent mutable state that survives updates.
- **Isolation:** a pack cannot reference files outside its own directory.
- **Swap the pack path in config (`RAW_PACK_PATH`) → a different agent.** That's the whole model.

## FAQ (answered permanently)
- **Add a moat later?** Yes — the moat is the pack's `validator`. The base is moat-agnostic.
- **Swap the database?** Yes — flip `RAW_VECTOR_PROVIDER` in config, or add an adapter once (reusable forever).
- **Rebuild per project?** No — build the base once; each project is just a new pack.
- **What's common?** ~80% (the base). What differs? ~20% (the pack).
