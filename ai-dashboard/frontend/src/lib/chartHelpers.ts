import type { TimeSeriesPoint } from "../types/api";
import { formatDateTime } from "./formatters";

export type AvailabilityChartPoint = {
  timestamp: string;
  label: string;
  visibleStores: number;
  deltaVisibleStores: number | null;
};

export function toAvailabilityChartData(points: TimeSeriesPoint[]): AvailabilityChartPoint[] {
  return points.map((point) => ({
    timestamp: point.timestamp,
    label: formatDateTime(point.timestamp),
    visibleStores: point.visible_stores,
    deltaVisibleStores: point.delta_visible_stores ?? null,
  }));
}
