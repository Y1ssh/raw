# How to build a pack (make a new agent)

Once the base is done, every new agent is a pack. Do NOT modify the base.

## Steps
1. Create a new repo `my-pack/` (or a folder under `packs/` while prototyping).
2. Add `pack.json` (manifest): name, version, and what it provides.
3. Add the components you need (all optional except the manifest):
   - `tools/` — MCP servers / @tool files (the actions)
   - `skills/` — SKILL.md workflows
   - `prompt.md` — the system prompt (persona)
   - `rules.md` — the limits
   - `theme/tokens.json` — the UI skin
   - `validator.py` — the quality gate (your moat)
4. Point the base at it: set `RAW_PACK_PATH=./my-pack` in `.env`.
5. Run `make dev`. The loader discovers, registers, and runs your pack.

## Example: the research pack (Grounded)
```
 research-pack/
 ├── pack.json                 # {"name":"research","version":"0.1.0",...}
 ├── tools/                    # search_corpus, find_papers, extract_table, cite
 ├── skills/prisma/SKILL.md    # literature-review workflow
 ├── prompt.md                 # "cite everything; abstain if you can't ground it"
 ├── rules.md                  # "never fabricate a citation"
 ├── theme/tokens.json         # evidence panels, trust-blue
 └── validator.py              # RAGAS faithfulness + source_recall  <- the moat
```

Swap the pack path to `./coding-pack` and the SAME base becomes a coding agent. That's the win.
