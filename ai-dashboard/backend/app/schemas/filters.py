from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


Granularity = Literal["raw", "10s", "1min", "5min", "15min", "1h", "hour", "day"]
SortDirection = Literal["asc", "desc"]
YScale = Literal["auto", "linear", "log"]
StoresTableSortBy = Literal[
    "entity_label",
    "avg_visible_stores",
    "min_visible_stores",
    "max_visible_stores",
    "stddev_visible_stores",
    "range_visible_stores",
    "points_count",
    "min_timestamp",
    "max_timestamp",
]


class AnalyticsFilters(BaseModel):
    start: datetime | None = None
    end: datetime | None = None
    metric: str | None = None
    source_file: str | None = None
    source_files: list[str] = Field(default_factory=list)
    granularity: Granularity = "1h"
    hour_from: int | None = Field(default=None, ge=0, le=23)
    hour_to: int | None = Field(default=None, ge=0, le=23)
    threshold_min: float | None = Field(default=None, ge=0)
    compare_previous: bool = False
    anomaly_drop_pct: float = Field(default=5.0, ge=0, le=100)
    y_scale: YScale = "auto"
    limit: int = Field(default=500, ge=1, le=5000)
    offset: int = Field(default=0, ge=0)
    sort_by: StoresTableSortBy = "stddev_visible_stores"
    sort_direction: SortDirection = "desc"
    bucket_count: int = Field(default=20, ge=2, le=100)

    @model_validator(mode="after")
    def validate_range(self) -> "AnalyticsFilters":
        if self.start and self.end and self.start > self.end:
            raise ValueError("start must be before end")
        if self.hour_from is not None and self.hour_to is not None and self.hour_from > self.hour_to:
            raise ValueError("hour_from must be less than or equal to hour_to")
        return self
