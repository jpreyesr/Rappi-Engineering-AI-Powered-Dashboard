from datetime import datetime
from typing import Any

from app.core.constants import (
    AVAILABILITY_ENRICHED_TABLE,
    AVAILABILITY_POINTS_TABLE,
    LOAD_METADATA_TABLE,
    MONITORING_WINDOWS_TABLE,
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
    GRANULARITY_BUCKETS = {
        "1min": "time_bucket(INTERVAL '1 minute', timestamp)",
        "5min": "time_bucket(INTERVAL '5 minutes', timestamp)",
        "15min": "time_bucket(INTERVAL '15 minutes', timestamp)",
        "1h": "date_trunc('hour', timestamp)",
        "hour": "date_trunc('hour', timestamp)",
        "day": "date_trunc('day', timestamp)",
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

    def monitoring_sources(self, filters: AnalyticsFilters | None = None) -> list[dict[str, Any]]:
        filters = filters or AnalyticsFilters()
        where_sql, params = self._window_where_clause(filters)
        rows = self.db.execute(
            f"""
            select
                source_file,
                metric,
                min_timestamp,
                max_timestamp,
                points_count,
                first_visible_stores,
                last_visible_stores,
                min_visible_stores,
                max_visible_stores,
                avg_visible_stores,
                stddev_visible_stores,
                behavior
            from {MONITORING_WINDOWS_TABLE}
            {where_sql}
            order by min_timestamp, source_file
            limit ?
            offset ?
            """,
            [*params, filters.limit, filters.offset],
        )
        return [
            {
                "entity_id": source_file,
                "entity_label": source_file,
                "metric": metric,
                "min_timestamp": min_timestamp,
                "max_timestamp": max_timestamp,
                "points_count": points_count,
                "first_visible_stores": first_visible_stores,
                "last_visible_stores": last_visible_stores,
                "min_visible_stores": min_visible_stores,
                "max_visible_stores": max_visible_stores,
                "avg_visible_stores": avg_visible_stores,
                "stddev_visible_stores": stddev_visible_stores,
                "range_visible_stores": (max_visible_stores - min_visible_stores)
                if max_visible_stores is not None and min_visible_stores is not None
                else None,
                "behavior": behavior,
            }
            for (
                source_file,
                metric,
                min_timestamp,
                max_timestamp,
                points_count,
                first_visible_stores,
                last_visible_stores,
                min_visible_stores,
                max_visible_stores,
                avg_visible_stores,
                stddev_visible_stores,
                behavior,
            ) in rows
        ]

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
                quantile_cont(visible_stores, 0.5) as p50_visible_stores,
                quantile_cont(visible_stores, 0.95) as p95_visible_stores,
                quantile_cont(visible_stores, 0.99) as p99_visible_stores,
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
            p50,
            p95,
            p99,
            min_timestamp,
            max_timestamp,
        ) = stats[0]
        first_rows = self.db.execute(
            f"""
            select visible_stores
            from {AVAILABILITY_POINTS_TABLE}
            {where_sql}
            order by timestamp asc
            limit 1
            """,
            params,
        )
        last_rows = self.db.execute(
            f"""
            select visible_stores
            from {AVAILABILITY_POINTS_TABLE}
            {where_sql}
            order by timestamp desc
            limit 1
            """,
            params,
        )
        first_value = first_rows[0][0] if first_rows else None
        last_value = last_rows[0][0] if last_rows else None
        absolute_change = last_value - first_value if first_value is not None and last_value is not None else None
        percent_change = (
            (absolute_change / first_value) * 100
            if absolute_change is not None and first_value not in (None, 0)
            else None
        )
        below_count = 0
        below_seconds = None
        if filters.threshold_min is not None:
            below_count, below_seconds = self.db.execute(
                f"""
                select count(*), sum(coalesce(interval_seconds, 10))
                from {AVAILABILITY_ENRICHED_TABLE}
                {where_sql}
                {'and' if where_sql else 'where'} visible_stores < ?
                """,
                [*params, filters.threshold_min],
            )[0]
        behaviors = self.db.execute(
            f"""
            select behavior, sum(points_count) as weight
            from {MONITORING_WINDOWS_TABLE}
            {self._window_where_clause(filters)[0]}
            group by behavior
            order by weight desc nulls last
            limit 1
            """,
            self._window_where_clause(filters)[1],
        )
        dominant_behavior = behaviors[0][0] if behaviors else None

        return {
            "latest_timestamp": latest_timestamp,
            "current_visible_stores": current,
            "previous_visible_stores": previous,
            "delta_visible_stores": delta,
            "first_visible_stores": first_value,
            "last_visible_stores": last_value,
            "absolute_change_visible_stores": absolute_change,
            "percent_change_visible_stores": percent_change,
            "average_visible_stores": average,
            "min_visible_stores": minimum,
            "max_visible_stores": maximum,
            "volatility_visible_stores": volatility,
            "p50_visible_stores": p50,
            "p95_visible_stores": p95,
            "p99_visible_stores": p99,
            "below_threshold_count": below_count or 0,
            "below_threshold_seconds": below_seconds,
            "dominant_behavior": dominant_behavior,
            "recommended_y_scale": self._recommended_y_scale(minimum, maximum),
            "points_count": points_count or 0,
            "min_timestamp": min_timestamp,
            "max_timestamp": max_timestamp,
        }

    def availability_trend(self, filters: AnalyticsFilters) -> list[dict[str, Any]]:
        where_sql, params = self._where_clause(filters)
        if filters.granularity in {"raw", "10s"}:
            rows = self.db.execute(
                f"""
                with percentiles as (
                    select
                        quantile_cont(visible_stores, 0.5) as p50,
                        quantile_cont(visible_stores, 0.95) as p95,
                        quantile_cont(visible_stores, 0.99) as p99
                    from {AVAILABILITY_POINTS_TABLE}
                    {where_sql}
                )
                select timestamp, visible_stores, delta_visible_stores, p50, p95, p99
                from {AVAILABILITY_ENRICHED_TABLE}, percentiles
                {where_sql}
                order by timestamp
                limit ?
                """,
                [*params, *params, filters.limit],
            )
        else:
            bucket_expr = self.GRANULARITY_BUCKETS[filters.granularity]
            rows = self.db.execute(
                f"""
                with percentiles as (
                    select
                        quantile_cont(visible_stores, 0.5) as p50,
                        quantile_cont(visible_stores, 0.95) as p95,
                        quantile_cont(visible_stores, 0.99) as p99
                    from {AVAILABILITY_POINTS_TABLE}
                    {where_sql}
                ),
                bucketed as (
                    select
                        {bucket_expr} as bucket,
                        avg(visible_stores) as visible_stores
                    from {AVAILABILITY_POINTS_TABLE}
                    {where_sql}
                    group by 1
                )
                select
                    bucket as timestamp,
                    visible_stores,
                    visible_stores - lag(visible_stores) over (order by bucket) as delta_visible_stores,
                    p50,
                    p95,
                    p99
                from bucketed, percentiles
                order by bucket
                limit ?
                """,
                [*params, *params, filters.limit],
            )

        return [
            {
                "timestamp": timestamp,
                "visible_stores": visible_stores,
                "delta_visible_stores": delta,
                "p50_visible_stores": p50,
                "p95_visible_stores": p95,
                "p99_visible_stores": p99,
            }
            for timestamp, visible_stores, delta, p50, p95, p99 in rows
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
        latest_rows = self.db.execute(
            f"""
            select visible_stores
            from {AVAILABILITY_POINTS_TABLE}
            {where_sql}
            order by timestamp desc
            limit 1
            """,
            params,
        )
        latest_value = latest_rows[0][0] if latest_rows else None
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
                        "contains_latest": True,
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
                    "contains_latest": latest_value is not None and bucket_start <= latest_value <= bucket_end,
                }
            )
        return {"total_count": total_count, "buckets": buckets}

    def stores_table(self, filters: AnalyticsFilters) -> dict[str, Any]:
        where_sql, params = self._window_where_clause(filters)
        sort_column = self.STORE_TABLE_SORT_COLUMNS[filters.sort_by]
        sort_direction = "asc" if filters.sort_direction == "asc" else "desc"
        total = self.db.execute(
            f"""
            select count(*)
            from {MONITORING_WINDOWS_TABLE}
            {where_sql}
            """,
            params,
        )[0][0]
        rows = self.db.execute(
            f"""
            with windows as (
                select
                    source_file as entity_id,
                    source_file as entity_label,
                    avg_visible_stores,
                    min_visible_stores,
                    max_visible_stores,
                    stddev_visible_stores,
                    max_visible_stores - min_visible_stores as range_visible_stores,
                    points_count,
                    min_timestamp,
                    max_timestamp,
                    first_visible_stores,
                    last_visible_stores,
                    behavior
                from {MONITORING_WINDOWS_TABLE}
                {where_sql}
            )
            select
                entity_id,
                entity_label,
                avg_visible_stores,
                min_visible_stores,
                max_visible_stores,
                stddev_visible_stores,
                range_visible_stores,
                points_count,
                min_timestamp,
                max_timestamp,
                first_visible_stores,
                last_visible_stores,
                behavior
            from windows
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
                    "first_visible_stores": first_visible_stores,
                    "last_visible_stores": last_visible_stores,
                    "behavior": behavior,
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
                    first_visible_stores,
                    last_visible_stores,
                    behavior,
                ) in rows
            ],
        }

    def delta_trend(self, filters: AnalyticsFilters) -> list[dict[str, Any]]:
        trend_filters = filters.model_copy()
        trend_points = self.availability_trend(trend_filters)
        rows: list[dict[str, Any]] = []
        previous: float | None = None
        for point in trend_points:
            current = point["visible_stores"]
            delta = current - previous if previous is not None else point.get("delta_visible_stores")
            delta_percent = (delta / previous) * 100 if delta is not None and previous not in (None, 0) else None
            rows.append(
                {
                    "timestamp": point["timestamp"],
                    "visible_stores": current,
                    "previous_visible_stores": previous,
                    "delta_visible_stores": delta,
                    "delta_percent": delta_percent,
                    "is_anomaly": delta_percent is not None and delta_percent <= -abs(filters.anomaly_drop_pct),
                }
            )
            previous = current
        return rows

    def hourly_heatmap(self, filters: AnalyticsFilters) -> dict[str, Any]:
        where_sql, params = self._where_clause(filters)
        rows = self.db.execute(
            f"""
            select
                cast(timestamp as date) as date_value,
                extract('hour' from timestamp) as hour_of_day,
                avg(visible_stores) as avg_visible_stores,
                count(*) as points_count
            from {AVAILABILITY_POINTS_TABLE}
            {where_sql}
            group by 1, 2
            order by 1, 2
            """,
            params,
        )
        cells = [
            {
                "date": str(date_value),
                "hour_of_day": int(hour_of_day),
                "avg_visible_stores": avg_visible_stores,
                "points_count": points_count,
            }
            for date_value, hour_of_day, avg_visible_stores, points_count in rows
        ]
        return {"days_count": len({cell["date"] for cell in cells}), "cells": cells}

    def period_comparison(self, filters: AnalyticsFilters) -> list[dict[str, Any]]:
        if not filters.start or not filters.end:
            metadata = self.load_metadata()
            filters = filters.model_copy(update={"start": metadata["min_timestamp"], "end": metadata["max_timestamp"]})
        if not filters.start or not filters.end:
            return []

        duration_seconds = int((filters.end - filters.start).total_seconds())
        previous_filters = filters.model_copy(
            update={
                "start": filters.start.fromtimestamp(filters.start.timestamp() - duration_seconds),
                "end": filters.end.fromtimestamp(filters.end.timestamp() - duration_seconds),
            }
        )
        current_points = self.availability_trend(filters)
        previous_points = self.availability_trend(previous_filters)
        rows: list[dict[str, Any]] = []
        for point in current_points:
            rows.append(
                {
                    "period_label": "actual",
                    "offset_seconds": int((point["timestamp"] - filters.start).total_seconds()),
                    "timestamp": point["timestamp"],
                    "visible_stores": point["visible_stores"],
                }
            )
        for point in previous_points:
            rows.append(
                {
                    "period_label": "anterior",
                    "offset_seconds": int((point["timestamp"] - previous_filters.start).total_seconds()),
                    "timestamp": point["timestamp"],
                    "visible_stores": point["visible_stores"],
                }
            )
        return rows

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
        if filters.source_files:
            placeholders = ", ".join("?" for _ in filters.source_files)
            clauses.append(f"{prefix}source_file in ({placeholders})")
            params.extend(filters.source_files)
        if filters.hour_from is not None:
            clauses.append(f"extract('hour' from {prefix}timestamp) >= ?")
            params.append(filters.hour_from)
        if filters.hour_to is not None:
            clauses.append(f"extract('hour' from {prefix}timestamp) <= ?")
            params.append(filters.hour_to)
        return (f"where {' and '.join(clauses)}" if clauses else "", params)

    def _window_where_clause(self, filters: AnalyticsFilters) -> tuple[str, list[Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if filters.start:
            clauses.append("max_timestamp >= ?")
            params.append(filters.start)
        if filters.end:
            clauses.append("min_timestamp <= ?")
            params.append(filters.end)
        if filters.metric:
            clauses.append("metric = ?")
            params.append(filters.metric)
        if filters.source_file:
            clauses.append("source_file = ?")
            params.append(filters.source_file)
        if filters.source_files:
            placeholders = ", ".join("?" for _ in filters.source_files)
            clauses.append(f"source_file in ({placeholders})")
            params.extend(filters.source_files)
        if filters.hour_from is not None:
            clauses.append("extract('hour' from min_timestamp) >= ?")
            params.append(filters.hour_from)
        if filters.hour_to is not None:
            clauses.append("extract('hour' from max_timestamp) <= ?")
            params.append(filters.hour_to)
        return (f"where {' and '.join(clauses)}" if clauses else "", params)

    def _recommended_y_scale(self, minimum: float | None, maximum: float | None) -> str:
        if minimum is None or maximum is None or minimum <= 0:
            return "linear"
        return "log" if maximum / minimum >= 100 else "linear"
