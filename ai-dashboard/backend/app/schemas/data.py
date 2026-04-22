from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


FileIngestionStatus = Literal[
    "loaded",
    "loaded_raw",
    "skipped_empty",
    "skipped_non_csv",
    "failed_parse",
    "failed_schema",
]


class IngestionFileReport(BaseModel):
    file_name: str
    status: FileIngestionStatus
    table_name: str | None = None
    rows_loaded: int = 0
    points_loaded: int = 0
    errors: list[str] = Field(default_factory=list)


class DataLoadResponse(BaseModel):
    status: str
    source_dir: str
    files_seen: int
    files_loaded: int
    files_skipped: int
    points_loaded: int
    tables_created: list[str]
    min_timestamp: datetime | None = None
    max_timestamp: datetime | None = None
    errors: list[str] = Field(default_factory=list)
    file_reports: list[IngestionFileReport] = Field(default_factory=list)


class DataStatusResponse(BaseModel):
    status: str
    source_dir: str
    files_seen: int = 0
    files_loaded: int = 0
    files_skipped: int = 0
    points_loaded: int = 0
    tables_created: list[str] = Field(default_factory=list)
    min_timestamp: datetime | None = None
    max_timestamp: datetime | None = None
    last_loaded_at: datetime | None = None
    errors: list[str] = Field(default_factory=list)
    recent_files: list[IngestionFileReport] = Field(default_factory=list)


class MonitoringSource(BaseModel):
    source_file: str
    metric: str | None = None
    min_timestamp: datetime | None = None
    max_timestamp: datetime | None = None
    points_count: int = 0
    first_visible_stores: float | None = None
    last_visible_stores: float | None = None
    min_visible_stores: float | None = None
    max_visible_stores: float | None = None
    avg_visible_stores: float | None = None
    stddev_visible_stores: float | None = None
    behavior: str = "unknown"


class DataSourcesResponse(BaseModel):
    total: int
    sources: list[MonitoringSource] = Field(default_factory=list)
