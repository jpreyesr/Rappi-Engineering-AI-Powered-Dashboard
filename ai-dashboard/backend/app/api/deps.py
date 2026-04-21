from functools import lru_cache

from app.core.config import get_settings
from app.db.duckdb_client import DuckDBClient
from app.repositories.analytics_repository import AnalyticsRepository
from app.services.analytics_service import AnalyticsService
from app.services.chat_service import ChatService
from app.services.ingestion_service import IngestionService


@lru_cache
def get_duckdb_client() -> DuckDBClient:
    settings = get_settings()
    return DuckDBClient(settings.resolved_duckdb_path)


@lru_cache
def get_analytics_repository() -> AnalyticsRepository:
    return AnalyticsRepository(get_duckdb_client())


@lru_cache
def get_analytics_service() -> AnalyticsService:
    return AnalyticsService(get_analytics_repository())


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(get_analytics_service(), get_settings())


@lru_cache
def get_ingestion_service() -> IngestionService:
    return IngestionService(get_duckdb_client())
