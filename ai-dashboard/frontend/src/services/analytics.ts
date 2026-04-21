import type { AvailabilitySummary, TimeSeriesResponse } from "../types/api";
import { apiGet } from "./api";

export function getAvailabilitySummary(): Promise<AvailabilitySummary> {
  return apiGet<AvailabilitySummary>("/analytics/summary");
}

export function getAvailabilityTimeseries(): Promise<TimeSeriesResponse> {
  return apiGet<TimeSeriesResponse>("/analytics/timeseries?granularity=hour&limit=500");
}
