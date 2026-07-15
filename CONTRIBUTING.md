# Contributing to Raw

## Golden rule
**Base vs pack.** Only add code here if it is COMMON to every agent. Anything domain-specific
(tools, prompts, validators, themes) belongs in a pack repo. When unsure, read `docs/BASE-VS-PACK.md`.

## Dev setup
```bash
cp .env.example .env
make up          # postgres + redis
make dev         # backend
make test        # pytest
make lint        # ruff + mypy
```

## Standards
- Python 3.12, `uv` for deps, `ruff` (lint+format), `mypy` (strict), `pytest`.
- Frontend: Next.js 15, TypeScript, eslint + prettier.
- Pre-commit hooks run ruff + mypy + a secret check. Install: `pre-commit install`.
- Every PR must pass CI (lint + type + test + build).
- Conventional commits encouraged. SemVer for releases.

## Never
- Never commit `.env` or any secret.
- Never hard-kill a process holding the DB open — use graceful shutdown (SIGTERM).
- Never bake a specific tool/prompt/validator into the base.
