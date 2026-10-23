import os
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine repository root (two levels up from backend/app/core)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BACKEND_DIR.parent
DEFAULT_DATASET_DIR = str(REPO_ROOT / "data" / "raw" / "ml-32m")


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    PROJECT_NAME: str = "CineGraph API"
    VERSION: str = "0.2.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # CORS configuration
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Database configuration
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "cinegraph_neo4j_secret_change_me"

    MONETDB_HOST: str = "localhost"
    MONETDB_PORT: int = 50000
    MONETDB_DATABASE: str = "cinegraph"
    MONETDB_USER: str = "monetdb"
    MONETDB_PASSWORD: str = "cinegraph_monetdb_secret_change_me"

    # Ingestion configuration
    DATASET_DIR: str = DEFAULT_DATASET_DIR
    INGESTION_BATCH_SIZE: int = 5000
    INGESTION_SAMPLE_LIMIT: int = 0  # 0 means full import, > 0 sets row/movie limit

    @property
    def resolved_dataset_dir(self) -> str:
        """Return absolute dataset directory path."""
        p = Path(self.DATASET_DIR)
        if not p.is_absolute():
            return str((REPO_ROOT / p).resolve())
        return str(p.resolve())

    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
