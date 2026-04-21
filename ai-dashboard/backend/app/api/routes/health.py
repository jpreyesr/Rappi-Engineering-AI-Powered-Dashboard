from fastapi import APIRouter, Depends

from app.api.deps import get_duckdb_client
from app.core.config import get_settings
from app.db.duckdb_client import DuckDBClient

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck(db: DuckDBClient = Depends(get_duckdb_client)) -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "duckdb_path": str(settings.resolved_duckdb_path),
        "duckdb_connected": db.ping(),
    }
