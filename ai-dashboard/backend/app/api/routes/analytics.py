from datetime import datetime

from fastapi import APIRouter, Body, Depends, Query

from app.api.deps import get_analytics_service
from app.schemas.analytics import (
    AnalyticsKpisResponse,
    AvailabilitySummary,
    AvailabilityTrendResponse,
    DistributionResponse,
    FilterOptionsResponse,
    StoresTableResponse,
    TimeSeriesResponse,
    TopUnstableStoresResponse,
)
from app.schemas.filters import AnalyticsFilters, Granularity
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["analytics"])


@router.get("/api/filters", response_model=FilterOptionsResponse)
def get_filters(service: AnalyticsService = Depends(get_analytics_service)) -> FilterOptionsResponse:
    return service.get_filter_options()


@router.post("/api/analytics/kpis", response_model=AnalyticsKpisResponse)
def get_kpis(
    filters: AnalyticsFilters = Body(default_factory=AnalyticsFilters),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsKpisResponse:
    return service.get_kpis(filters)


@router.post("/api/analytics/availability-trend", response_model=AvailabilityTrendResponse)
def get_availability_trend(
    filters: AnalyticsFilters = Body(default_factory=AnalyticsFilters),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AvailabilityTrendResponse:
    return service.get_availability_trend(filters)


@router.post("/api/analytics/top-unstable-stores", response_model=TopUnstableStoresResponse)
def get_top_unstable_stores(
    filters: AnalyticsFilters = Body(default_factory=AnalyticsFilters),
    service: AnalyticsService = Depends(get_analytics_service),
) -> TopUnstableStoresResponse:
    return service.get_top_unstable_stores(filters)


@router.post("/api/analytics/distribution", response_model=DistributionResponse)
def get_distribution(
    filters: AnalyticsFilters = Body(default_factory=AnalyticsFilters),
    service: AnalyticsService = Depends(get_analytics_service),
) -> DistributionResponse:
    return service.get_distribution(filters)


@router.post("/api/analytics/stores-table", response_model=StoresTableResponse)
def get_stores_table(
    filters: AnalyticsFilters = Body(default_factory=AnalyticsFilters),
    service: AnalyticsService = Depends(get_analytics_service),
) -> StoresTableResponse:
    return service.get_stores_table(filters)


@router.get("/analytics/summary", response_model=AvailabilitySummary)
def get_summary(
    start: datetime | None = None,
    end: datetime | None = None,
    service: AnalyticsService = Depends(get_analytics_service),
) -> AvailabilitySummary:
    return service.get_summary(AnalyticsFilters(start=start, end=end))


@router.get("/analytics/timeseries", response_model=TimeSeriesResponse)
def get_timeseries(
    start: datetime | None = None,
    end: datetime | None = None,
    granularity: Granularity = "hour",
    limit: int = Query(default=500, ge=1, le=5000),
    service: AnalyticsService = Depends(get_analytics_service),
) -> TimeSeriesResponse:
    filters = AnalyticsFilters(start=start, end=end, granularity=granularity, limit=limit)
    return service.get_timeseries(filters)
