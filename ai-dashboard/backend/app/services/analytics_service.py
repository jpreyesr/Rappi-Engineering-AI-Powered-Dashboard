from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    AnalyticsKpisResponse,
    AvailabilitySummary,
    AvailabilityTrendResponse,
    DatasetMetadata,
    DeltaTrendPoint,
    DeltaTrendResponse,
    DistributionBucket,
    DistributionResponse,
    FilterOptionsResponse,
    HeatmapCell,
    HourlyHeatmapResponse,
    Kpi,
    PeriodComparisonPoint,
    PeriodComparisonResponse,
    StoresTableResponse,
    StoresTableRow,
    TimeSeriesPoint,
    TimeSeriesResponse,
    TopUnstableStoresResponse,
    UnstableEntity,
)
from app.schemas.filters import AnalyticsFilters


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository

    def get_filter_options(self) -> FilterOptionsResponse:
        options = self.repository.filter_options()
        return FilterOptionsResponse(
            min_timestamp=options["min_timestamp"],
            max_timestamp=options["max_timestamp"],
            metrics=options["metrics"],
            source_files=options["source_files"],
            granularities=["raw", "10s", "1min", "5min", "15min", "1h", "hour", "day"],
        )

    def get_kpis(self, filters: AnalyticsFilters | None = None) -> AnalyticsKpisResponse:
        filters = self._normalize_filters(filters)
        stats = self.repository.kpis(filters)
        return AnalyticsKpisResponse(**stats)

    def get_availability_trend(self, filters: AnalyticsFilters | None = None) -> AvailabilityTrendResponse:
        filters = self._normalize_filters(filters, default_limit=500)
        points = [TimeSeriesPoint(**point) for point in self.repository.availability_trend(filters)]
        return AvailabilityTrendResponse(granularity=filters.granularity, points=points)

    def get_top_unstable_stores(self, filters: AnalyticsFilters | None = None) -> TopUnstableStoresResponse:
        filters = self._normalize_filters(filters, default_limit=10)
        items = [UnstableEntity(**item) for item in self.repository.top_unstable_sources(filters)]
        return TopUnstableStoresResponse(items=items)

    def get_distribution(self, filters: AnalyticsFilters | None = None) -> DistributionResponse:
        filters = self._normalize_filters(filters)
        result = self.repository.distribution(filters)
        buckets = [DistributionBucket(**bucket) for bucket in result["buckets"]]
        return DistributionResponse(
            bucket_count=filters.bucket_count,
            total_count=result["total_count"],
            buckets=buckets,
        )

    def get_stores_table(self, filters: AnalyticsFilters | None = None) -> StoresTableResponse:
        filters = self._normalize_filters(filters, default_limit=50)
        result = self.repository.stores_table(filters)
        rows = [StoresTableRow(**row) for row in result["rows"]]
        return StoresTableResponse(total=result["total"], limit=filters.limit, offset=filters.offset, rows=rows)

    def get_monitoring_windows(self, filters: AnalyticsFilters | None = None) -> StoresTableResponse:
        return self.get_stores_table(filters)

    def get_delta_trend(self, filters: AnalyticsFilters | None = None) -> DeltaTrendResponse:
        filters = self._normalize_filters(filters, default_limit=500)
        points = [DeltaTrendPoint(**point) for point in self.repository.delta_trend(filters)]
        return DeltaTrendResponse(granularity=filters.granularity, anomaly_drop_pct=filters.anomaly_drop_pct, points=points)

    def get_hourly_heatmap(self, filters: AnalyticsFilters | None = None) -> HourlyHeatmapResponse:
        filters = self._normalize_filters(filters)
        result = self.repository.hourly_heatmap(filters)
        return HourlyHeatmapResponse(
            days_count=result["days_count"],
            cells=[HeatmapCell(**cell) for cell in result["cells"]],
        )

    def get_period_comparison(self, filters: AnalyticsFilters | None = None) -> PeriodComparisonResponse:
        filters = self._normalize_filters(filters, default_limit=500)
        points = [PeriodComparisonPoint(**point) for point in self.repository.period_comparison(filters)]
        return PeriodComparisonResponse(granularity=filters.granularity, points=points)

    def get_summary(self, filters: AnalyticsFilters | None = None) -> AvailabilitySummary:
        filters = self._normalize_filters(filters)
        metadata = DatasetMetadata(**self.repository.load_metadata())
        stats = self.repository.summary_stats(filters)

        current = stats["current_visible_stores"]
        average = stats["average_visible_stores"]
        delta = stats["delta_visible_stores"]
        maximum = stats["max_visible_stores"]

        kpis = [
            Kpi(
                label="Visible stores now",
                value=round(current) if current is not None else None,
                helper="Latest point in DuckDB",
            ),
            Kpi(
                label="Average visible stores",
                value=round(average) if average is not None else None,
                helper="Average over the selected range",
            ),
            Kpi(
                label="Latest delta",
                value=round(delta) if delta is not None else None,
                helper="Change versus previous point",
            ),
            Kpi(
                label="Peak visible stores",
                value=round(maximum) if maximum is not None else None,
                helper="Maximum in the selected range",
            ),
        ]

        return AvailabilitySummary(
            metadata=metadata,
            kpis=kpis,
            latest_timestamp=stats["latest_timestamp"],
            current_visible_stores=stats["current_visible_stores"],
            previous_visible_stores=stats["previous_visible_stores"],
            delta_visible_stores=stats["delta_visible_stores"],
            average_visible_stores=stats["average_visible_stores"],
            min_visible_stores=stats["min_visible_stores"],
            max_visible_stores=stats["max_visible_stores"],
        )

    def get_timeseries(self, filters: AnalyticsFilters | None = None) -> TimeSeriesResponse:
        trend = self.get_availability_trend(filters)
        return TimeSeriesResponse(granularity=trend.granularity, points=trend.points)

    def compact_context(self) -> dict:
        filters = self._normalize_filters(None)
        kpis = self.get_kpis(filters)
        metadata = DatasetMetadata(**self.repository.load_metadata())
        return {
            "current_visible_stores": kpis.current_visible_stores,
            "average_visible_stores": kpis.average_visible_stores,
            "delta_visible_stores": kpis.delta_visible_stores,
            "min_visible_stores": kpis.min_visible_stores,
            "max_visible_stores": kpis.max_visible_stores,
            "volatility_visible_stores": kpis.volatility_visible_stores,
            "p50_visible_stores": kpis.p50_visible_stores,
            "p95_visible_stores": kpis.p95_visible_stores,
            "p99_visible_stores": kpis.p99_visible_stores,
            "dominant_behavior": kpis.dominant_behavior,
            "recommended_y_scale": kpis.recommended_y_scale,
            "points_count": kpis.points_count,
            "latest_timestamp": kpis.max_timestamp.isoformat() if kpis.max_timestamp else None,
            "files_count": metadata.files_count,
            "min_timestamp": metadata.min_timestamp.isoformat() if metadata.min_timestamp else None,
            "max_timestamp": metadata.max_timestamp.isoformat() if metadata.max_timestamp else None,
        }

    def _normalize_filters(
        self,
        filters: AnalyticsFilters | None,
        default_limit: int | None = None,
    ) -> AnalyticsFilters:
        filters = filters or AnalyticsFilters()
        if default_limit is not None and filters.limit == AnalyticsFilters().limit:
            filters.limit = default_limit
        if filters.metric:
            return filters

        options = self.repository.filter_options()
        if len(options["metrics"]) == 1:
            filters.metric = options["metrics"][0]
        return filters
