import type {
  AnalyticsFilters,
  AnalyticsKpisResponse,
  AvailabilitySummary,
  AvailabilityTrendResponse,
  DataSourcesResponse,
  DeltaTrendResponse,
  DistributionResponse,
  FilterOptionsResponse,
  HourlyHeatmapResponse,
  PeriodComparisonResponse,
  StoresTableResponse,
  TimeSeriesResponse,
  TopUnstableStoresResponse,
} from "../types/api";
import { apiGet, apiPost } from "./api";

export function getFilterOptions(): Promise<FilterOptionsResponse> {
  return apiGet<FilterOptionsResponse>("/api/filters");
}

export function getAnalyticsKpis(filters: AnalyticsFilters): Promise<AnalyticsKpisResponse> {
  return apiPost<AnalyticsKpisResponse, AnalyticsFilters>("/api/analytics/kpis", filters);
}

export function getAvailabilityTrend(filters: AnalyticsFilters): Promise<AvailabilityTrendResponse> {
  return apiPost<AvailabilityTrendResponse, AnalyticsFilters>("/api/analytics/availability-trend", filters);
}

export function getDeltaTrend(filters: AnalyticsFilters): Promise<DeltaTrendResponse> {
  return apiPost<DeltaTrendResponse, AnalyticsFilters>("/api/analytics/delta-trend", filters);
}

export function getHourlyHeatmap(filters: AnalyticsFilters): Promise<HourlyHeatmapResponse> {
  return apiPost<HourlyHeatmapResponse, AnalyticsFilters>("/api/analytics/hourly-heatmap", filters);
}

export function getPeriodComparison(filters: AnalyticsFilters): Promise<PeriodComparisonResponse> {
  return apiPost<PeriodComparisonResponse, AnalyticsFilters>("/api/analytics/period-comparison", filters);
}

export function getTopUnstableStores(filters: AnalyticsFilters): Promise<TopUnstableStoresResponse> {
  return apiPost<TopUnstableStoresResponse, AnalyticsFilters>("/api/analytics/top-unstable-stores", filters);
}

export function getDistribution(filters: AnalyticsFilters): Promise<DistributionResponse> {
  return apiPost<DistributionResponse, AnalyticsFilters>("/api/analytics/distribution", filters);
}

export function getStoresTable(filters: AnalyticsFilters): Promise<StoresTableResponse> {
  return apiPost<StoresTableResponse, AnalyticsFilters>("/api/analytics/monitoring-windows", filters);
}

export function getDataSources(): Promise<DataSourcesResponse> {
  return apiGet<DataSourcesResponse>("/api/data/sources");
}

export function getAvailabilitySummary(): Promise<AvailabilitySummary> {
  return apiGet<AvailabilitySummary>("/analytics/summary");
}

export function getAvailabilityTimeseries(): Promise<TimeSeriesResponse> {
  return apiGet<TimeSeriesResponse>("/analytics/timeseries?granularity=hour&limit=500");
}
