"""Agent endpoints (chat / stream / threads).

TODO (Sprint 3): chat endpoint -> queue -> worker -> SSE stream (reasoning + tool cards + answer).
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["agent"])
