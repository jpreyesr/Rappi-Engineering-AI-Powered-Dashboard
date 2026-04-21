from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    AvailabilitySummary,
    DatasetMetadata,
    Kpi,
    TimeSeriesPoint,
    TimeSeriesResponse,
)
from app.schemas.filters import AnalyticsFilters


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository

    def get_summary(self, filters: AnalyticsFilters | None = None) -> AvailabilitySummary:
        filters = filters or AnalyticsFilters()
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

        return AvailabilitySummary(metadata=metadata, kpis=kpis, **stats)

    def get_timeseries(self, filters: AnalyticsFilters | None = None) -> TimeSeriesResponse:
        filters = filters or AnalyticsFilters()
        points = [TimeSeriesPoint(**point) for point in self.repository.timeseries(filters)]
        return TimeSeriesResponse(granularity=filters.granularity, points=points)

    def compact_context(self) -> dict:
        summary = self.get_summary()
        return {
            "current_visible_stores": summary.current_visible_stores,
            "average_visible_stores": summary.average_visible_stores,
            "delta_visible_stores": summary.delta_visible_stores,
            "min_visible_stores": summary.min_visible_stores,
            "max_visible_stores": summary.max_visible_stores,
            "latest_timestamp": summary.latest_timestamp.isoformat() if summary.latest_timestamp else None,
            "files_count": summary.metadata.files_count,
            "points_count": summary.metadata.points_count,
            "min_timestamp": summary.metadata.min_timestamp.isoformat() if summary.metadata.min_timestamp else None,
            "max_timestamp": summary.metadata.max_timestamp.isoformat() if summary.metadata.max_timestamp else None,
        }
