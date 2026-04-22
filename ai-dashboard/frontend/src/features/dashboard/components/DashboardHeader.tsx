import { Database, RefreshCw } from "lucide-react";

import { formatDateTime, formatNumber } from "../../../lib/formatters";
import type { AnalyticsKpisResponse, FilterOptionsResponse } from "../types";

type DashboardHeaderProps = {
  options: FilterOptionsResponse | null;
  kpis: AnalyticsKpisResponse | null;
  isLoading: boolean;
  sourcesCount?: number;
};

export function DashboardHeader({ options, kpis, isLoading, sourcesCount }: DashboardHeaderProps) {
  return (
    <header className="flex flex-col gap-4 border-b border-neutral-200 pb-5 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <h1 className="mt-1 text-3xl font-semibold tracking-normal text-neutral-950">AI-Powered Availability Dashboard</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-neutral-600">
          Análisis de disponibilidad de tiendas con filtros, gráficos y conversación sobre los datos cargados.
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-700">
          <Database className="h-4 w-4 text-emerald-700" aria-hidden="true" />
          {kpis ? `${formatNumber(kpis.points_count)} puntos` : "Cargando dataset"}
        </div>
        <div className="flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-700">
          <Database className="h-4 w-4 text-blue-700" aria-hidden="true" />
          {formatNumber(sourcesCount ?? null)} ventanas
        </div>
        <div className="flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-700">
          <RefreshCw className={isLoading ? "h-4 w-4 animate-spin text-blue-700" : "h-4 w-4 text-blue-700"} />
          {formatDateTime(options?.min_timestamp ?? null)} - {formatDateTime(options?.max_timestamp ?? null)}
        </div>
      </div>
    </header>
  );
}
