from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


Granularity = Literal["raw", "hour", "day"]


class AnalyticsFilters(BaseModel):
    start: datetime | None = None
    end: datetime | None = None
    granularity: Granularity = "hour"
    limit: int = Field(default=500, ge=1, le=5000)

    @model_validator(mode="after")
    def validate_range(self) -> "AnalyticsFilters":
        if self.start and self.end and self.start > self.end:
            raise ValueError("start must be before end")
        return self
