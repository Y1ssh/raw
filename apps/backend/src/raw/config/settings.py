"""Config-over-code: every SLOT is selected here from the environment.

Swapping a value (model, vector DB, pack path) changes the agent WITHOUT touching code.
Settings are validated on startup — misconfiguration fails fast.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAW_", env_file=".env", extra="ignore")

    env: str = "dev"
    log_level: str = "INFO"

    llm_model: str = "ollama/qwen2.5:3b"
    llm_fallback: str = ""

    postgres_url: str = "postgresql://raw:raw@localhost:5432/raw"
    redis_url: str = "redis://localhost:6379/0"

    vector_provider: str = "pgvector"  # pgvector | qdrant | none

    max_iterations: int = 10  # hard loop cap — no infinite loops

    pack_path: str = "./example-pack"  # swap this -> a different agent


@lru_cache
def get_settings() -> Settings:
    return Settings()
