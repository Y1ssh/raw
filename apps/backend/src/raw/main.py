"""Raw backend entrypoint. FastAPI app wiring the base together.

Sprint 0: health + config load (fail fast). Later sprints add the agent routes, streaming,
queue, observability. Run: `make dev`.
"""

import logging

from fastapi import FastAPI

from raw import __version__
from raw.api import health, routes
from raw.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()  # validates config on startup — fail fast
    logging.basicConfig(level=settings.log_level)
    app = FastAPI(title="Raw", version=__version__)
    app.include_router(health.router)
    app.include_router(routes.router)
    return app


app = create_app()
