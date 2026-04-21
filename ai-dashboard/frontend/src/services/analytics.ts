import type {
  AnalyticsFilters,
  AnalyticsKpisResponse,
  AvailabilitySummary,
  AvailabilityTrendResponse,
  DistributionResponse,
  FilterOptionsResponse,
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

export function getTopUnstableStores(filters: AnalyticsFilters): Promise<TopUnstableStoresResponse> {
  return apiPost<TopUnstableStoresResponse, AnalyticsFilters>("/api/analytics/top-unstable-stores", filters);
}

export function getDistribution(filters: AnalyticsFilters): Promise<DistributionResponse> {
  return apiPost<DistributionResponse, AnalyticsFilters>("/api/analytics/distribution", filters);
}

export function getStoresTable(filters: AnalyticsFilters): Promise<StoresTableResponse> {
  return apiPost<StoresTableResponse, AnalyticsFilters>("/api/analytics/stores-table", filters);
}

export function getAvailabilitySummary(): Promise<AvailabilitySummary> {
  return apiGet<AvailabilitySummary>("/analytics/summary");
}

export function getAvailabilityTimeseries(): Promise<TimeSeriesResponse> {
  return apiGet<TimeSeriesResponse>("/analytics/timeseries?granularity=hour&limit=500");
}
