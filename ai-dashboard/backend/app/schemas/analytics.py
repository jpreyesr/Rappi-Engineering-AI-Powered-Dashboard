from datetime import datetime

from pydantic import BaseModel


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


class TimeSeriesResponse(BaseModel):
    granularity: str
    points: list[TimeSeriesPoint]
