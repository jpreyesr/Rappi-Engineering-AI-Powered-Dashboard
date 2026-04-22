import { CalendarClock } from "lucide-react";

import { formatCompactNumber } from "../../../lib/formatters";
import type { HourlyHeatmapResponse } from "../types";
import { EmptyState, LoadingBlock } from "./StateBlocks";

type HourlyHeatmapProps = {
  heatmap: HourlyHeatmapResponse | null;
  isLoading: boolean;
};

export function HourlyHeatmap({ heatmap, isLoading }: HourlyHeatmapProps) {
  const cells = heatmap?.cells ?? [];
  const values = cells.map((cell) => cell.avg_visible_stores ?? 0);
  const max = Math.max(...values, 0);
  const dates = Array.from(new Set(cells.map((cell) => cell.date)));
  const hours = Array.from({ length: 24 }, (_, index) => index);

  return (
    <article className="rounded-md border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <CalendarClock className="h-5 w-5 text-violet-700" aria-hidden="true" />
        <div>
          <h2 className="text-lg font-semibold text-neutral-950">Patrón por hora y día</h2>
          <p className="mt-1 text-sm text-neutral-500">Promedio de tiendas visibles por fecha y hora.</p>
        </div>
      </div>

      {isLoading && cells.length === 0 ? <LoadingBlock className="h-[260px]" /> : null}
      {!isLoading && cells.length === 0 ? (
        <EmptyState title="Sin heatmap" description="No hay suficientes puntos para construir el patrón horario." />
      ) : null}
      {!isLoading && (heatmap?.days_count ?? 0) < 2 && cells.length > 0 ? (
        <p className="mb-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          Hay datos de un solo día. El heatmap funciona, pero será más útil al cargar más ventanas de otros días.
        </p>
      ) : null}
      {cells.length > 0 ? (
        <div className="overflow-x-auto">
          <div className="grid min-w-[760px] gap-1" style={{ gridTemplateColumns: "92px repeat(24, minmax(22px, 1fr))" }}>
            <div />
            {hours.map((hour) => (
              <div key={hour} className="text-center text-[10px] font-medium text-neutral-500">
                {hour}
              </div>
            ))}
            {dates.map((date) => (
              <>
                <div key={`${date}-label`} className="truncate pr-2 text-xs font-medium text-neutral-600">
                  {date}
                </div>
                {hours.map((hour) => {
                  const cell = cells.find((item) => item.date === date && item.hour_of_day === hour);
                  const value = cell?.avg_visible_stores ?? null;
                  const intensity = value && max > 0 ? Math.max(value / max, 0.08) : 0;
                  return (
                    <div
                      key={`${date}-${hour}`}
                      title={value ? `${date} ${hour}:00 · ${formatCompactNumber(value)}` : `${date} ${hour}:00 · sin datos`}
                      className="h-7 rounded-sm border border-white"
                      style={{ backgroundColor: value ? `rgba(5, 150, 105, ${intensity})` : "#f5f5f5" }}
                    />
                  );
                })}
              </>
            ))}
          </div>
        </div>
      ) : null}
    </article>
  );
}
