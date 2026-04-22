#!/usr/bin/env sh
set -e

cd /app/backend

if [ ! -f "/app/data/processed/dashboard.duckdb" ]; then
  echo "DuckDB not found. Loading CSVs from /app/data/extracted..."
  python - <<'PY'
from app.api.deps import get_duckdb_client
from app.services.ingestion_service import IngestionService

service = IngestionService(get_duckdb_client())
result = service.load()
print(f"Loaded {result.points_loaded} points from {result.files_loaded} files.")
PY
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
