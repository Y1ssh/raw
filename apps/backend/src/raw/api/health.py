"""Health + readiness endpoints. (Ops basics from day 1.)"""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness — the process is up."""
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str]:
    """Readiness — TODO (Sprint 1): check Postgres + Redis connectivity."""
    return {"status": "ready"}
