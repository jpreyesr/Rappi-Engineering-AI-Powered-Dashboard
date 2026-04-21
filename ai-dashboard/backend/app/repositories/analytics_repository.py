from datetime import datetime
from typing import Any

from app.core.constants import (
    AVAILABILITY_ENRICHED_TABLE,
    AVAILABILITY_POINTS_TABLE,
    LOAD_METADATA_TABLE,
)
from app.db.duckdb_client import DuckDBClient
from app.schemas.filters import AnalyticsFilters


class AnalyticsRepository:
    def __init__(self, db: DuckDBClient) -> None:
        self.db = db

    def load_metadata(self) -> dict[str, Any]:
        rows = self.db.execute(
            f"""
            select loaded_at, files_count, points_count, min_timestamp, max_timestamp, errors
            from {LOAD_METADATA_TABLE}
            order by loaded_at desc
            limit 1
            """
        )
        if not rows:
            return {
                "loaded_at": None,
                "files_count": 0,
                "points_count": 0,
                "min_timestamp": None,
                "max_timestamp": None,
                "errors": None,
            }

        loaded_at, files_count, points_count, min_timestamp, max_timestamp, errors = rows[0]
        return {
            "loaded_at": loaded_at,
            "files_count": files_count,
            "points_count": points_count,
            "min_timestamp": min_timestamp,
            "max_timestamp": max_timestamp,
            "errors": errors or None,
        }

    def summary_stats(self, filters: AnalyticsFilters) -> dict[str, Any]:
        where_sql, params = self._where_clause(filters)
        current_rows = self.db.execute(
            f"""
            select timestamp, visible_stores, previous_visible_stores, delta_visible_stores
            from {AVAILABILITY_ENRICHED_TABLE}
            {where_sql}
            order by timestamp desc
            limit 1
            """,
            params,
        )
        aggregate_rows = self.db.execute(
            f"""
            select avg(visible_stores), min(visible_stores), max(visible_stores)
            from {AVAILABILITY_POINTS_TABLE}
            {where_sql}
            """,
            params,
        )

        latest_timestamp = None
        current = None
        previous = None
        delta = None
        if current_rows:
            latest_timestamp, current, previous, delta = current_rows[0]

        average, minimum, maximum = aggregate_rows[0] if aggregate_rows else (None, None, None)
        return {
            "latest_timestamp": latest_timestamp,
            "current_visible_stores": current,
            "previous_visible_stores": previous,
            "delta_visible_stores": delta,
            "average_visible_stores": average,
            "min_visible_stores": minimum,
            "max_visible_stores": maximum,
        }

    def timeseries(self, filters: AnalyticsFilters) -> list[dict[str, Any]]:
        where_sql, params = self._where_clause(filters)
        if filters.granularity == "raw":
            rows = self.db.execute(
                f"""
                select timestamp, visible_stores
                from {AVAILABILITY_POINTS_TABLE}
                {where_sql}
                order by timestamp
                limit ?
                """,
                [*params, filters.limit],
            )
        else:
            trunc_unit = "day" if filters.granularity == "day" else "hour"
            rows = self.db.execute(
                f"""
                select date_trunc('{trunc_unit}', timestamp) as bucket, avg(visible_stores) as visible_stores
                from {AVAILABILITY_POINTS_TABLE}
                {where_sql}
                group by 1
                order by 1
                limit ?
                """,
                [*params, filters.limit],
            )

        return [{"timestamp": timestamp, "visible_stores": visible_stores} for timestamp, visible_stores in rows]

    def _where_clause(self, filters: AnalyticsFilters) -> tuple[str, list[datetime]]:
        clauses: list[str] = []
        params: list[datetime] = []
        if filters.start:
            clauses.append("timestamp >= ?")
            params.append(filters.start)
        if filters.end:
            clauses.append("timestamp <= ?")
            params.append(filters.end)
        return (f"where {' and '.join(clauses)}" if clauses else "", params)
