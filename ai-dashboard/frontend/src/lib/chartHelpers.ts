import type { TimeSeriesPoint } from "../types/api";
import { formatDateTime } from "./formatters";

export type AvailabilityChartPoint = {
  timestamp: string;
  label: string;
  visibleStores: number;
  deltaVisibleStores: number | null;
  p50VisibleStores: number | null;
  p95VisibleStores: number | null;
  p99VisibleStores: number | null;
  isAnomaly: boolean;
};

export function toAvailabilityChartData(points: TimeSeriesPoint[]): AvailabilityChartPoint[] {
  return points.map((point) => ({
    timestamp: point.timestamp,
    label: formatDateTime(point.timestamp),
    visibleStores: point.visible_stores,
    deltaVisibleStores: point.delta_visible_stores ?? null,
    p50VisibleStores: point.p50_visible_stores ?? null,
    p95VisibleStores: point.p95_visible_stores ?? null,
    p99VisibleStores: point.p99_visible_stores ?? null,
    isAnomaly: point.is_anomaly ?? false,
  }));
}
