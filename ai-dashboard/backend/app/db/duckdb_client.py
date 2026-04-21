from pathlib import Path
from typing import Any

import duckdb
from duckdb import DuckDBPyConnection


class DuckDBClient:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def connect(self, read_only: bool = True) -> DuckDBPyConnection:
        if not read_only:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
        if read_only and not self.database_path.exists():
            raise FileNotFoundError(f"DuckDB database not found at {self.database_path}")
        return duckdb.connect(str(self.database_path), read_only=read_only)

    def execute(
        self,
        query: str,
        params: list[Any] | tuple[Any, ...] | None = None,
        read_only: bool = True,
    ) -> list[tuple[Any, ...]]:
        if not self.database_path.exists():
            raise FileNotFoundError(f"DuckDB database not found at {self.database_path}")

        with self.connect(read_only=read_only) as connection:
            return connection.execute(query, params or []).fetchall()

    def execute_script(self, script: str, read_only: bool = False) -> None:
        with self.connect(read_only=read_only) as connection:
            connection.execute(script)

    def ping(self) -> bool:
        rows = self.execute("select 1")
        return rows == [(1,)]
