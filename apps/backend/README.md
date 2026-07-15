# Raw backend

FastAPI + LangGraph. The base harness.

```bash
uv sync            # install (pinned deps)
uv run pytest -q   # tests
uv run uvicorn raw.main:app --reload --port 8077
```

## Layout
- `core/`   — the 30-line loop + LangGraph graph + typed state
- `slots/`  — swappable layers (llm, memory, vector, tools, guardrails, observability)
- `packs/`  — the pack loader + contract (the seam)
- `api/`    — FastAPI routes (health now; chat/stream later)
- `config/` — pydantic-settings (the slot selector)
