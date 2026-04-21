from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


DASHBOARD_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "AI-Powered Dashboard"
    app_env: str = "local"
    duckdb_path: Path = Field(default=Path("data/processed/dashboard.duckdb"))
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    model_name: str | None = None
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=(DASHBOARD_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def resolved_duckdb_path(self) -> Path:
        if self.duckdb_path.is_absolute():
            return self.duckdb_path
        return DASHBOARD_ROOT / self.duckdb_path

    @property
    def resolved_model_name(self) -> str:
        return self.model_name or self.openai_model


@lru_cache
def get_settings() -> Settings:
    return Settings()
