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
    average_visible_stores: float | None
    min_visible_stores: float | None
    max_visible_stores: float | None
    volatility_visible_stores: float | None
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


class StoresTableResponse(BaseModel):
    total: int
    limit: int
    offset: int
    rows: list[StoresTableRow]
