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
};

export type TimeSeriesResponse = {
  granularity: "raw" | "hour" | "day";
  points: TimeSeriesPoint[];
};

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatResponse = {
  answer: string;
  used_ai: boolean;
  tool_calls: Array<{ name: string; arguments: Record<string, unknown> }>;
};
