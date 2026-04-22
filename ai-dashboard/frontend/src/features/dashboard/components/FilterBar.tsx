import { RotateCcw } from "lucide-react";

import type { FilterOptionsResponse, Granularity } from "../types";

type FilterState = {
  startDate: string;
  endDate: string;
  sourceFiles: string[];
  granularity: Granularity;
  hourFrom: string;
  hourTo: string;
  thresholdMin: string;
  comparePrevious: boolean;
  anomalyDropPct: string;
  yScale: "auto" | "linear" | "log";
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
    <section className="surface-panel rounded-lg border p-4">
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Inicio</span>
          <input
            type="date"
            value={filters.startDate}
            min={options?.min_timestamp?.slice(0, 10) ?? undefined}
            max={filters.endDate || options?.max_timestamp?.slice(0, 10) || undefined}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ startDate: event.target.value })}
            className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition disabled:bg-slate-100"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Fin</span>
          <input
            type="date"
            value={filters.endDate}
            min={filters.startDate || options?.min_timestamp?.slice(0, 10) || undefined}
            max={options?.max_timestamp?.slice(0, 10) ?? undefined}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ endDate: event.target.value })}
            className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition disabled:bg-slate-100"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Períodos observados</span>
          <select
            value={filters.sourceFiles}
            multiple
            disabled={isLoading}
            onChange={(event) =>
              onChange({ sourceFiles: Array.from(event.currentTarget.selectedOptions).map((option) => option.value) })
            }
            className="h-24 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition disabled:bg-slate-100"
          >
            {(options?.source_files ?? []).map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Granularidad</span>
          <select
            value={filters.granularity}
            disabled={isLoading}
            onChange={(event) => onChange({ granularity: event.currentTarget.value as Granularity })}
            className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition disabled:bg-slate-100"
          >
            {(options?.granularities ?? ["raw", "hour", "day"]).map((granularity) => (
              <option key={granularity} value={granularity}>
                {granularity === "raw" ? "10s nativo" : granularity}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Hora desde</span>
          <input
            type="number"
            min={0}
            max={23}
            value={filters.hourFrom}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ hourFrom: event.target.value })}
            className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition disabled:bg-slate-100"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Hora hasta</span>
          <input
            type="number"
            min={0}
            max={23}
            value={filters.hourTo}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ hourTo: event.target.value })}
            className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition disabled:bg-slate-100"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Umbral mínimo</span>
          <input
            type="number"
            min={0}
            value={filters.thresholdMin}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ thresholdMin: event.target.value })}
            className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition disabled:bg-slate-100"
          />
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Escala Y</span>
          <select
            value={filters.yScale}
            disabled={isLoading}
            onChange={(event) => onChange({ yScale: event.currentTarget.value as "auto" | "linear" | "log" })}
            className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition disabled:bg-slate-100"
          >
            <option value="auto">Automática</option>
            <option value="linear">Lineal</option>
            <option value="log">Logarítmica</option>
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block font-medium text-slate-700">Caída anómala %</span>
          <input
            type="number"
            min={0}
            max={100}
            value={filters.anomalyDropPct}
            disabled={isLoading}
            onChange={(event: { target: { value: string } }) => onChange({ anomalyDropPct: event.target.value })}
            className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition disabled:bg-slate-100"
          />
        </label>
        <label className="flex items-end gap-2 pb-2 text-sm font-medium text-slate-700">
          <input
            type="checkbox"
            checked={filters.comparePrevious}
            disabled={isLoading}
            onChange={(event: { target: { checked: boolean } }) => onChange({ comparePrevious: event.target.checked })}
            className="h-4 w-4 rounded border-slate-300 text-orange-600 focus:ring-orange-200"
          />
          Comparar período anterior
        </label>
        <div className="flex items-end justify-end">
          <button
            type="button"
            onClick={onReset}
            disabled={isLoading}
            className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-orange-200 bg-orange-50 text-orange-700 transition hover:bg-orange-100 disabled:cursor-not-allowed disabled:opacity-60"
            title="Reiniciar filtros"
            aria-label="Reiniciar filtros"
          >
            <RotateCcw className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </div>
    </section>
  );
}
