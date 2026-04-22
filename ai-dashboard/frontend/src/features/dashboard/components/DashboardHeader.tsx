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
    <header className="rounded-lg border border-orange-100 bg-white/75 p-5 shadow-[0_18px_45px_rgba(15,23,42,0.06)] backdrop-blur lg:flex lg:items-end lg:justify-between">
      <div>
        <h1 className="text-3xl font-semibold tracking-normal text-slate-950">Prueba Rappi - AI-Powered Dashboard</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Explora cuántas tiendas estuvieron visibles, cuándo hubo caídas o picos, y qué tan estable fue la disponibilidad.
        </p>
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-2 lg:mt-0">
        <div className="flex items-center gap-2 rounded-md border border-orange-100 bg-orange-50 px-3 py-2 text-sm font-medium text-orange-900">
          <Database className="h-4 w-4 text-orange-600" aria-hidden="true" />
          {kpis ? `${formatNumber(kpis.points_count)} puntos` : "Cargando dataset"}
        </div>
        <div className="flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
          <Database className="h-4 w-4 text-slate-500" aria-hidden="true" />
          {formatNumber(sourcesCount ?? null)} períodos
        </div>
        <div className="flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">
          <RefreshCw className={isLoading ? "h-4 w-4 animate-spin text-orange-600" : "h-4 w-4 text-orange-600"} />
          {formatDateTime(options?.min_timestamp ?? null)} - {formatDateTime(options?.max_timestamp ?? null)}
        </div>
      </div>
    </header>
  );
}
