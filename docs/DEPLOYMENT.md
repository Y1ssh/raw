# Deployment

Start simple. Add complexity only when needed.

## Spectrum
| Stage | Use |
|---|---|
| Docker Compose | local dev (`make up`) |
| Dokploy (self-host PaaS) | small self-hosted deploy on any VPS |
| Kubernetes + KEDA + Argo | scale (KEDA scales workers on queue length) |

## Deploy the whole SYSTEM (not just the model)
Five homes, each scales independently:
- orchestration (FastAPI + LangGraph) — CPU, scales with users
- model backend (API / Ollama / vLLM) — GPU if self-host, scales with LLM calls
- tools / MCP servers — sandboxed
- data/state (Postgres + Redis + vector) — stateful
- observability (Langfuse)

## Cloud vs self-host vs hybrid
- Cloud = fast default. Self-host = privacy + cost-at-scale (crossover ~few-hundred LLM calls/day).
- Keep it PORTABLE (containers) so you can move between them.

## CI/CD
GitHub Actions: lint + type + test + build. AI is non-deterministic -> add eval-testing + canary
releases (ship a prompt/model change to a small % of traffic, watch quality, auto-rollback).
