from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_analytics_service
from app.schemas.analytics import AvailabilitySummary, TimeSeriesResponse
from app.schemas.filters import AnalyticsFilters, Granularity
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AvailabilitySummary)
def get_summary(
    start: datetime | None = None,
    end: datetime | None = None,
    service: AnalyticsService = Depends(get_analytics_service),
) -> AvailabilitySummary:
    return service.get_summary(AnalyticsFilters(start=start, end=end))


@router.get("/timeseries", response_model=TimeSeriesResponse)
def get_timeseries(
    start: datetime | None = None,
    end: datetime | None = None,
    granularity: Granularity = "hour",
    limit: int = Query(default=500, ge=1, le=5000),
    service: AnalyticsService = Depends(get_analytics_service),
) -> TimeSeriesResponse:
    filters = AnalyticsFilters(start=start, end=end, granularity=granularity, limit=limit)
    return service.get_timeseries(filters)
