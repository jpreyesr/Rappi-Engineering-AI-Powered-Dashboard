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
};

export type TimeSeriesResponse = {
  granularity: "raw" | "hour" | "day";
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

export type Granularity = "raw" | "hour" | "day";

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
  granularity?: Granularity;
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
  average_visible_stores: number | null;
  min_visible_stores: number | null;
  max_visible_stores: number | null;
  volatility_visible_stores: number | null;
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
};

export type StoresTableResponse = {
  total: number;
  limit: number;
  offset: number;
  rows: StoresTableRow[];
};
