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
    STORE_TABLE_SORT_COLUMNS = {
        "entity_label": "entity_label",
        "avg_visible_stores": "avg_visible_stores",
        "min_visible_stores": "min_visible_stores",
        "max_visible_stores": "max_visible_stores",
        "stddev_visible_stores": "stddev_visible_stores",
        "range_visible_stores": "range_visible_stores",
        "points_count": "points_count",
        "min_timestamp": "min_timestamp",
        "max_timestamp": "max_timestamp",
    }

    def __init__(self, db: DuckDBClient) -> None:
        self.db = db

    def filter_options(self) -> dict[str, Any]:
        metadata = self.load_metadata()
        metrics = [row[0] for row in self.db.execute(f"select distinct metric from {AVAILABILITY_POINTS_TABLE} order by 1")]
        source_files = [
            row[0] for row in self.db.execute(f"select distinct source_file from {AVAILABILITY_POINTS_TABLE} order by 1")
        ]
        return {
            "min_timestamp": metadata["min_timestamp"],
            "max_timestamp": metadata["max_timestamp"],
            "metrics": metrics,
            "source_files": source_files,
        }

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
            "points_count": files_count and points_count or 0,
            "min_timestamp": min_timestamp,
            "max_timestamp": max_timestamp,
            "errors": errors or None,
        }

    def kpis(self, filters: AnalyticsFilters) -> dict[str, Any]:
        where_sql, params = self._where_clause(filters)
        latest = self.db.execute(
            f"""
            select timestamp, visible_stores, previous_visible_stores, delta_visible_stores
            from {AVAILABILITY_ENRICHED_TABLE}
            {where_sql}
            order by timestamp desc
            limit 1
            """,
            params,
        )
        stats = self.db.execute(
            f"""
            select
                count(*) as points_count,
                avg(visible_stores) as average_visible_stores,
                min(visible_stores) as min_visible_stores,
                max(visible_stores) as max_visible_stores,
                stddev_samp(visible_stores) as volatility_visible_stores,
                min(timestamp) as min_timestamp,
                max(timestamp) as max_timestamp
            from {AVAILABILITY_POINTS_TABLE}
            {where_sql}
            """,
            params,
        )

        latest_timestamp = None
        current = None
        previous = None
        delta = None
        if latest:
            latest_timestamp, current, previous, delta = latest[0]

        (
            points_count,
            average,
            minimum,
            maximum,
            volatility,
            min_timestamp,
            max_timestamp,
        ) = stats[0]

        return {
            "latest_timestamp": latest_timestamp,
            "current_visible_stores": current,
            "previous_visible_stores": previous,
            "delta_visible_stores": delta,
            "average_visible_stores": average,
            "min_visible_stores": minimum,
            "max_visible_stores": maximum,
            "volatility_visible_stores": volatility,
            "points_count": points_count or 0,
            "min_timestamp": min_timestamp,
            "max_timestamp": max_timestamp,
        }

    def availability_trend(self, filters: AnalyticsFilters) -> list[dict[str, Any]]:
        where_sql, params = self._where_clause(filters)
        if filters.granularity == "raw":
            rows = self.db.execute(
                f"""
                select timestamp, visible_stores, delta_visible_stores
                from {AVAILABILITY_ENRICHED_TABLE}
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
                with bucketed as (
                    select
                        date_trunc('{trunc_unit}', timestamp) as bucket,
                        avg(visible_stores) as visible_stores
                    from {AVAILABILITY_POINTS_TABLE}
                    {where_sql}
                    group by 1
                )
                select
                    bucket as timestamp,
                    visible_stores,
                    visible_stores - lag(visible_stores) over (order by bucket) as delta_visible_stores
                from bucketed
                order by bucket
                limit ?
                """,
                [*params, filters.limit],
            )

        return [
            {"timestamp": timestamp, "visible_stores": visible_stores, "delta_visible_stores": delta}
            for timestamp, visible_stores, delta in rows
        ]

    def top_unstable_sources(self, filters: AnalyticsFilters) -> list[dict[str, Any]]:
        where_sql, params = self._where_clause(filters, table_alias="p")
        rows = self.db.execute(
            f"""
            with source_points as (
                select
                    p.source_file,
                    p.timestamp,
                    p.visible_stores,
                    p.visible_stores - lag(p.visible_stores) over (
                        partition by p.source_file, p.metric
                        order by p.timestamp
                    ) as source_delta
                from {AVAILABILITY_POINTS_TABLE} p
                {where_sql}
            )
            select
                source_file as entity_id,
                source_file as entity_label,
                avg(visible_stores) as avg_visible_stores,
                min(visible_stores) as min_visible_stores,
                max(visible_stores) as max_visible_stores,
                stddev_samp(visible_stores) as stddev_visible_stores,
                max(visible_stores) - min(visible_stores) as range_visible_stores,
                avg(abs(source_delta)) as avg_abs_delta_visible_stores,
                max(abs(source_delta)) as max_abs_delta_visible_stores,
                count(*) as points_count,
                min(timestamp) as min_timestamp,
                max(timestamp) as max_timestamp
            from source_points
            group by source_file
            order by stddev_visible_stores desc nulls last, range_visible_stores desc nulls last
            limit ?
            """,
            [*params, filters.limit],
        )
        return [
            {
                "entity_id": entity_id,
                "entity_label": entity_label,
                "avg_visible_stores": avg_value,
                "min_visible_stores": min_value,
                "max_visible_stores": max_value,
                "stddev_visible_stores": stddev_value,
                "range_visible_stores": range_value,
                "avg_abs_delta_visible_stores": avg_abs_delta,
                "max_abs_delta_visible_stores": max_abs_delta,
                "points_count": points_count,
                "min_timestamp": min_timestamp,
                "max_timestamp": max_timestamp,
            }
            for (
                entity_id,
                entity_label,
                avg_value,
                min_value,
                max_value,
                stddev_value,
                range_value,
                avg_abs_delta,
                max_abs_delta,
                points_count,
                min_timestamp,
                max_timestamp,
            ) in rows
        ]

    def distribution(self, filters: AnalyticsFilters) -> dict[str, Any]:
        where_sql, params = self._where_clause(filters)
        stats = self.db.execute(
            f"""
            select min(visible_stores), max(visible_stores), count(*)
            from {AVAILABILITY_POINTS_TABLE}
            {where_sql}
            """,
            params,
        )[0]
        min_value, max_value, total_count = stats
        if not total_count or min_value is None or max_value is None:
            return {"total_count": 0, "buckets": []}

        if min_value == max_value:
            return {
                "total_count": total_count,
                "buckets": [
                    {
                        "bucket_index": 0,
                        "bucket_start": min_value,
                        "bucket_end": max_value,
                        "count": total_count,
                        "percentage": 100.0,
                    }
                ],
            }

        rows = self.db.execute(
            f"""
            with bounded as (
                select
                    least(
                        cast(floor(((visible_stores - ?) / nullif(? - ?, 0)) * ?) as integer),
                        ? - 1
                    ) as bucket_index
                from {AVAILABILITY_POINTS_TABLE}
                {where_sql}
            )
            select bucket_index, count(*) as count
            from bounded
            group by 1
            order by 1
            """,
            [min_value, max_value, min_value, filters.bucket_count, filters.bucket_count, *params],
        )
        bucket_width = (max_value - min_value) / filters.bucket_count
        buckets = []
        for bucket_index, count in rows:
            bucket_start = min_value + (bucket_width * bucket_index)
            bucket_end = max_value if bucket_index == filters.bucket_count - 1 else bucket_start + bucket_width
            buckets.append(
                {
                    "bucket_index": bucket_index,
                    "bucket_start": bucket_start,
                    "bucket_end": bucket_end,
                    "count": count,
                    "percentage": (count / total_count) * 100,
                }
            )
        return {"total_count": total_count, "buckets": buckets}

    def stores_table(self, filters: AnalyticsFilters) -> dict[str, Any]:
        where_sql, params = self._where_clause(filters)
        sort_column = self.STORE_TABLE_SORT_COLUMNS[filters.sort_by]
        sort_direction = "asc" if filters.sort_direction == "asc" else "desc"
        total = self.db.execute(
            f"""
            select count(distinct source_file)
            from {AVAILABILITY_POINTS_TABLE}
            {where_sql}
            """,
            params,
        )[0][0]
        rows = self.db.execute(
            f"""
            select
                source_file as entity_id,
                source_file as entity_label,
                avg(visible_stores) as avg_visible_stores,
                min(visible_stores) as min_visible_stores,
                max(visible_stores) as max_visible_stores,
                stddev_samp(visible_stores) as stddev_visible_stores,
                max(visible_stores) - min(visible_stores) as range_visible_stores,
                count(*) as points_count,
                min(timestamp) as min_timestamp,
                max(timestamp) as max_timestamp
            from {AVAILABILITY_POINTS_TABLE}
            {where_sql}
            group by source_file
            order by {sort_column} {sort_direction} nulls last
            limit ?
            offset ?
            """,
            [*params, filters.limit, filters.offset],
        )
        return {
            "total": total or 0,
            "rows": [
                {
                    "entity_id": entity_id,
                    "entity_label": entity_label,
                    "avg_visible_stores": avg_value,
                    "min_visible_stores": min_value,
                    "max_visible_stores": max_value,
                    "stddev_visible_stores": stddev_value,
                    "range_visible_stores": range_value,
                    "points_count": points_count,
                    "min_timestamp": min_timestamp,
                    "max_timestamp": max_timestamp,
                }
                for (
                    entity_id,
                    entity_label,
                    avg_value,
                    min_value,
                    max_value,
                    stddev_value,
                    range_value,
                    points_count,
                    min_timestamp,
                    max_timestamp,
                ) in rows
            ],
        }

    def summary_stats(self, filters: AnalyticsFilters) -> dict[str, Any]:
        return self.kpis(filters)

    def timeseries(self, filters: AnalyticsFilters) -> list[dict[str, Any]]:
        return self.availability_trend(filters)

    def _where_clause(
        self,
        filters: AnalyticsFilters,
        table_alias: str | None = None,
    ) -> tuple[str, list[Any]]:
        prefix = f"{table_alias}." if table_alias else ""
        clauses: list[str] = []
        params: list[Any] = []
        if filters.start:
            clauses.append(f"{prefix}timestamp >= ?")
            params.append(filters.start)
        if filters.end:
            clauses.append(f"{prefix}timestamp <= ?")
            params.append(filters.end)
        if filters.metric:
            clauses.append(f"{prefix}metric = ?")
            params.append(filters.metric)
        if filters.source_file:
            clauses.append(f"{prefix}source_file = ?")
            params.append(filters.source_file)
        return (f"where {' and '.join(clauses)}" if clauses else "", params)
