from pathlib import Path
from typing import Any

import duckdb


class DuckDBClient:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def execute(self, query: str, params: list[Any] | tuple[Any, ...] | None = None) -> list[tuple[Any, ...]]:
        if not self.database_path.exists():
            raise FileNotFoundError(f"DuckDB database not found at {self.database_path}")

        with duckdb.connect(str(self.database_path), read_only=True) as connection:
            return connection.execute(query, params or []).fetchall()

    def ping(self) -> bool:
        rows = self.execute("select 1")
        return rows == [(1,)]
