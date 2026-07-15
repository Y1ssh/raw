# ---- build stage ----
FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project
COPY . .
RUN uv sync --no-dev

# ---- runtime stage ----
FROM python:3.12-slim AS runtime
WORKDIR /app
RUN useradd -m app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"
USER app
EXPOSE 8077
# Graceful shutdown: uvicorn handles SIGTERM -> never hard-kill state-holding processes.
CMD ["uvicorn", "raw.main:app", "--host", "0.0.0.0", "--port", "8077"]
