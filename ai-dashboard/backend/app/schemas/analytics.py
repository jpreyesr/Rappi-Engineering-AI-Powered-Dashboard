from datetime import datetime

from pydantic import BaseModel

from app.schemas.filters import Granularity


class DatasetMetadata(BaseModel):
    loaded_at: datetime | None
    files_count: int
    points_count: int
    min_timestamp: datetime | None
    max_timestamp: datetime | None
    errors: str | None = None


class Kpi(BaseModel):
    label: str
    value: float | int | str | None
    unit: str | None = None
    helper: str | None = None


class AvailabilitySummary(BaseModel):
    metadata: DatasetMetadata
    current_visible_stores: float | None
    previous_visible_stores: float | None
    delta_visible_stores: float | None
    average_visible_stores: float | None
    min_visible_stores: float | None
    max_visible_stores: float | None
    latest_timestamp: datetime | None
    kpis: list[Kpi]


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    visible_stores: float
    delta_visible_stores: float | None = None
    p50_visible_stores: float | None = None
    p95_visible_stores: float | None = None
    p99_visible_stores: float | None = None
    is_anomaly: bool = False


class TimeSeriesResponse(BaseModel):
    granularity: str
    points: list[TimeSeriesPoint]


class FilterOptionsResponse(BaseModel):
    min_timestamp: datetime | None
    max_timestamp: datetime | None
    metrics: list[str]
    source_files: list[str]
    granularities: list[Granularity]


class AnalyticsKpisResponse(BaseModel):
    current_visible_stores: float | None
    previous_visible_stores: float | None
    delta_visible_stores: float | None
    first_visible_stores: float | None = None
    last_visible_stores: float | None = None
    absolute_change_visible_stores: float | None = None
    percent_change_visible_stores: float | None = None
    average_visible_stores: float | None
    min_visible_stores: float | None
    max_visible_stores: float | None
    volatility_visible_stores: float | None
    p50_visible_stores: float | None = None
    p95_visible_stores: float | None = None
    p99_visible_stores: float | None = None
    below_threshold_count: int = 0
    below_threshold_seconds: float | None = None
    dominant_behavior: str | None = None
    recommended_y_scale: str = "linear"
    points_count: int
    min_timestamp: datetime | None
    max_timestamp: datetime | None


class AvailabilityTrendResponse(BaseModel):
    granularity: Granularity
    points: list[TimeSeriesPoint]


class UnstableEntity(BaseModel):
    entity_id: str
    entity_label: str
    entity_type: str = "source_file"
    avg_visible_stores: float | None
    min_visible_stores: float | None
    max_visible_stores: float | None
    stddev_visible_stores: float | None
    range_visible_stores: float | None
    avg_abs_delta_visible_stores: float | None
    max_abs_delta_visible_stores: float | None
    points_count: int
    min_timestamp: datetime | None
    max_timestamp: datetime | None


class TopUnstableStoresResponse(BaseModel):
    entity_type: str = "source_file"
    items: list[UnstableEntity]


class DistributionBucket(BaseModel):
    bucket_index: int
    bucket_start: float
    bucket_end: float
    count: int
    percentage: float
    contains_latest: bool = False


class DistributionResponse(BaseModel):
    bucket_count: int
    total_count: int
    buckets: list[DistributionBucket]


class StoresTableRow(BaseModel):
    entity_id: str
    entity_label: str
    entity_type: str = "source_file"
    avg_visible_stores: float | None
    min_visible_stores: float | None
    max_visible_stores: float | None
    stddev_visible_stores: float | None
    range_visible_stores: float | None
    points_count: int
    min_timestamp: datetime | None
    max_timestamp: datetime | None
    first_visible_stores: float | None = None
    last_visible_stores: float | None = None
    behavior: str | None = None


class StoresTableResponse(BaseModel):
    total: int
    limit: int
    offset: int
    rows: list[StoresTableRow]


class DeltaTrendPoint(BaseModel):
    timestamp: datetime
    visible_stores: float
    previous_visible_stores: float | None = None
    delta_visible_stores: float | None = None
    delta_percent: float | None = None
    is_anomaly: bool = False


class DeltaTrendResponse(BaseModel):
    granularity: Granularity
    anomaly_drop_pct: float
    points: list[DeltaTrendPoint]


class HeatmapCell(BaseModel):
    date: str
    hour_of_day: int
    avg_visible_stores: float | None
    points_count: int


class HourlyHeatmapResponse(BaseModel):
    cells: list[HeatmapCell]
    days_count: int


class PeriodComparisonPoint(BaseModel):
    period_label: str
    offset_seconds: int
    timestamp: datetime
    visible_stores: float


class PeriodComparisonResponse(BaseModel):
    granularity: Granularity
    points: list[PeriodComparisonPoint]
