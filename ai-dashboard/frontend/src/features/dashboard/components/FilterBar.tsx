import { RotateCcw } from "lucide-react";

import type { FilterOptionsResponse, Granularity } from "../types";

type FilterState = {
  startDate: string;
  endDate: string;
  metric: string;
  sourceFile: string;
  granularity: Granularity;
};

type FilterBarProps = {
  filters: FilterState;
  options: FilterOptionsResponse | null;
  isLoading: boolean;
  onChange: (next: Partial<FilterState>) => void;
  onReset: () => void;
};

export function FilterBar({ filters, options, isLoading, onChange, onReset }: FilterBarProps) {
  return (
    <section className="rounded-md border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-[1fr_1fr_1.2fr_1.4fr_0.8fr_auto]">
        <label className="text-sm">
          <span className="mb-1 block font-medium text-neutral-700">Start</span>
          <input
            type="date"
            value={filters.startDate}
            min={options?.min_timestamp?.slice(0, 10) ?? undefined}
            max={filters.endDate || options?.max_timestamp?.slice(0, 10) || undefined}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ startDate: event.target.value })}
            className="h-10 w-full rounded-md border border-neutral-300 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 disabled:bg-neutral-100"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-neutral-700">End</span>
          <input
            type="date"
            value={filters.endDate}
            min={filters.startDate || options?.min_timestamp?.slice(0, 10) || undefined}
            max={options?.max_timestamp?.slice(0, 10) ?? undefined}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ endDate: event.target.value })}
            className="h-10 w-full rounded-md border border-neutral-300 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 disabled:bg-neutral-100"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-neutral-700">Metric</span>
          <select
            value={filters.metric}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ metric: event.target.value })}
            className="h-10 w-full rounded-md border border-neutral-300 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 disabled:bg-neutral-100"
          >
            {(options?.metrics ?? []).map((metric) => (
              <option key={metric} value={metric}>
                {metric}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-neutral-700">Source window</span>
          <select
            value={filters.sourceFile}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ sourceFile: event.target.value })}
            className="h-10 w-full rounded-md border border-neutral-300 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 disabled:bg-neutral-100"
          >
            <option value="">All sources</option>
            {(options?.source_files ?? []).map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-neutral-700">Granularity</span>
          <select
            value={filters.granularity}
            disabled={isLoading}
            onChange={(event: { target: { value: Granularity } }) => onChange({ granularity: event.target.value })}
            className="h-10 w-full rounded-md border border-neutral-300 bg-white px-3 text-sm text-neutral-900 outline-none focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100 disabled:bg-neutral-100"
          >
            {(options?.granularities ?? ["raw", "hour", "day"]).map((granularity) => (
              <option key={granularity} value={granularity}>
                {granularity}
              </option>
            ))}
          </select>
        </label>
        <div className="flex items-end">
          <button
            type="button"
            onClick={onReset}
            disabled={isLoading}
            className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-neutral-300 bg-white text-neutral-700 transition hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
            title="Reset filters"
            aria-label="Reset filters"
          >
            <RotateCcw className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>
    </section>
  );
}
