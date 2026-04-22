export type DatasetMetadata = {
  loaded_at: string | null;
  files_count: number;
  points_count: number;
  min_timestamp: string | null;
  max_timestamp: string | null;
  errors: string | null;
};

export type Kpi = {
  label: string;
  value: number | string | null;
  unit: string | null;
  helper: string | null;
};

export type AvailabilitySummary = {
  metadata: DatasetMetadata;
  current_visible_stores: number | null;
  previous_visible_stores: number | null;
  delta_visible_stores: number | null;
  average_visible_stores: number | null;
  min_visible_stores: number | null;
  max_visible_stores: number | null;
  latest_timestamp: string | null;
  kpis: Kpi[];
};

export type TimeSeriesPoint = {
  timestamp: string;
  visible_stores: number;
  delta_visible_stores?: number | null;
  p50_visible_stores?: number | null;
  p95_visible_stores?: number | null;
  p99_visible_stores?: number | null;
  is_anomaly?: boolean;
};

export type TimeSeriesResponse = {
  granularity: Granularity;
  points: TimeSeriesPoint[];
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatRequest = {
  message: string;
  filters?: AnalyticsFilters;
  history?: ChatMessage[];
};

export type ChatResponse = {
  answer: string;
  used_ai: boolean;
  tool_calls: Array<{ name: string; arguments: Record<string, unknown> }>;
};

export type ChatSuggestionsResponse = {
  suggestions: string[];
};

export type Granularity = "raw" | "10s" | "1min" | "5min" | "15min" | "1h" | "hour" | "day";
export type YScale = "auto" | "linear" | "log";

export type SortDirection = "asc" | "desc";

export type StoresTableSortBy =
  | "entity_label"
  | "avg_visible_stores"
  | "min_visible_stores"
  | "max_visible_stores"
  | "stddev_visible_stores"
  | "range_visible_stores"
  | "points_count"
  | "min_timestamp"
  | "max_timestamp";

export type AnalyticsFilters = {
  start?: string | null;
  end?: string | null;
  metric?: string | null;
  source_file?: string | null;
  source_files?: string[];
  granularity?: Granularity;
  hour_from?: number | null;
  hour_to?: number | null;
  threshold_min?: number | null;
  compare_previous?: boolean;
  anomaly_drop_pct?: number;
  y_scale?: YScale;
  limit?: number;
  offset?: number;
  sort_by?: StoresTableSortBy;
  sort_direction?: SortDirection;
  bucket_count?: number;
};

export type FilterOptionsResponse = {
  min_timestamp: string | null;
  max_timestamp: string | null;
  metrics: string[];
  source_files: string[];
  granularities: Granularity[];
};

export type AnalyticsKpisResponse = {
  current_visible_stores: number | null;
  previous_visible_stores: number | null;
  delta_visible_stores: number | null;
  first_visible_stores: number | null;
  last_visible_stores: number | null;
  absolute_change_visible_stores: number | null;
  percent_change_visible_stores: number | null;
  average_visible_stores: number | null;
  min_visible_stores: number | null;
  max_visible_stores: number | null;
  volatility_visible_stores: number | null;
  p50_visible_stores: number | null;
  p95_visible_stores: number | null;
  p99_visible_stores: number | null;
  below_threshold_count: number;
  below_threshold_seconds: number | null;
  dominant_behavior: string | null;
  recommended_y_scale: string;
  points_count: number;
  min_timestamp: string | null;
  max_timestamp: string | null;
};

export type AvailabilityTrendResponse = {
  granularity: Granularity;
  points: TimeSeriesPoint[];
};

export type UnstableEntity = {
  entity_id: string;
  entity_label: string;
  entity_type: "source_file";
  avg_visible_stores: number | null;
  min_visible_stores: number | null;
  max_visible_stores: number | null;
  stddev_visible_stores: number | null;
  range_visible_stores: number | null;
  avg_abs_delta_visible_stores: number | null;
  max_abs_delta_visible_stores: number | null;
  points_count: number;
  min_timestamp: string | null;
  max_timestamp: string | null;
};

export type TopUnstableStoresResponse = {
  entity_type: "source_file";
  items: UnstableEntity[];
};

export type DistributionBucket = {
  bucket_index: number;
  bucket_start: number;
  bucket_end: number;
  count: number;
  percentage: number;
  contains_latest?: boolean;
};

export type DistributionResponse = {
  bucket_count: number;
  total_count: number;
  buckets: DistributionBucket[];
};

export type StoresTableRow = {
  entity_id: string;
  entity_label: string;
  entity_type: "source_file";
  avg_visible_stores: number | null;
  min_visible_stores: number | null;
  max_visible_stores: number | null;
  stddev_visible_stores: number | null;
  range_visible_stores: number | null;
  points_count: number;
  min_timestamp: string | null;
  max_timestamp: string | null;
  first_visible_stores?: number | null;
  last_visible_stores?: number | null;
  behavior?: string | null;
};

export type StoresTableResponse = {
  total: number;
  limit: number;
  offset: number;
  rows: StoresTableRow[];
};

export type DeltaTrendPoint = {
  timestamp: string;
  visible_stores: number;
  previous_visible_stores: number | null;
  delta_visible_stores: number | null;
  delta_percent: number | null;
  is_anomaly: boolean;
};

export type DeltaTrendResponse = {
  granularity: Granularity;
  anomaly_drop_pct: number;
  points: DeltaTrendPoint[];
};

export type HeatmapCell = {
  date: string;
  hour_of_day: number;
  avg_visible_stores: number | null;
  points_count: number;
};

export type HourlyHeatmapResponse = {
  cells: HeatmapCell[];
  days_count: number;
};

export type PeriodComparisonPoint = {
  period_label: string;
  offset_seconds: number;
  timestamp: string;
  visible_stores: number;
};

export type PeriodComparisonResponse = {
  granularity: Granularity;
  points: PeriodComparisonPoint[];
};

export type MonitoringSource = {
  source_file: string;
  metric: string | null;
  min_timestamp: string | null;
  max_timestamp: string | null;
  points_count: number;
  first_visible_stores: number | null;
  last_visible_stores: number | null;
  min_visible_stores: number | null;
  max_visible_stores: number | null;
  avg_visible_stores: number | null;
  stddev_visible_stores: number | null;
  behavior: string;
};

export type DataSourcesResponse = {
  total: number;
  sources: MonitoringSource[];
};
