from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


Granularity = Literal["raw", "hour", "day"]
SortDirection = Literal["asc", "desc"]
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
    granularity: Granularity = "hour"
    limit: int = Field(default=500, ge=1, le=5000)
    offset: int = Field(default=0, ge=0)
    sort_by: StoresTableSortBy = "stddev_visible_stores"
    sort_direction: SortDirection = "desc"
    bucket_count: int = Field(default=20, ge=2, le=100)

    @model_validator(mode="after")
    def validate_range(self) -> "AnalyticsFilters":
        if self.start and self.end and self.start > self.end:
            raise ValueError("start must be before end")
        return self
