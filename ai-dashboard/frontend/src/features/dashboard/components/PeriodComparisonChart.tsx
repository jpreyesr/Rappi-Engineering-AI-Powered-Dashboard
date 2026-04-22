import { GitCompare } from "lucide-react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { formatCompactNumber, formatNumber } from "../../../lib/formatters";
import type { PeriodComparisonResponse } from "../types";
import { EmptyState, LoadingBlock } from "./StateBlocks";

type PeriodComparisonChartProps = {
  comparison: PeriodComparisonResponse | null;
  isLoading: boolean;
};

export function PeriodComparisonChart({ comparison, isLoading }: PeriodComparisonChartProps) {
  const dataByOffset = new Map<number, { offset: number; label: string; actual?: number; anterior?: number }>();
  for (const point of comparison?.points ?? []) {
    const current = dataByOffset.get(point.offset_seconds) ?? {
      offset: point.offset_seconds,
      label: formatOffset(point.offset_seconds),
    };
    if (point.period_label === "actual") {
      current.actual = point.visible_stores;
    } else {
      current.anterior = point.visible_stores;
    }
    dataByOffset.set(point.offset_seconds, current);
  }
  const data = Array.from(dataByOffset.values()).sort((left, right) => left.offset - right.offset);

  return (
    <article className="rounded-lg border p-4">
      <div className="mb-4 flex items-center gap-2">
        <GitCompare className="h-5 w-5 text-orange-600" aria-hidden="true" />
        <div>
          <h2 className="text-lg font-semibold text-slate-950">Comparación de disponibilidad</h2>
          <p className="mt-1 text-sm text-slate-500">Compara tiendas visibles del período actual contra el anterior.</p>
        </div>
      </div>

      {isLoading && data.length === 0 ? <LoadingBlock className="h-[320px]" /> : null}
      {!isLoading && data.length === 0 ? (
        <EmptyState title="Sin comparación" description="Selecciona un rango con inicio y fin para comparar períodos." />
      ) : null}
      {data.length > 0 ? (
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" />
              <XAxis dataKey="label" minTickGap={28} tick={{ fontSize: 12, fill: "#525252" }} />
              <YAxis tickFormatter={formatCompactNumber} width={72} tick={{ fontSize: 12, fill: "#525252" }} />
              <Tooltip formatter={(value: unknown, name: unknown) => [formatNumber(Number(value)), name === "actual" ? "Actual" : "Anterior"]} />
              <Line type="monotone" dataKey="actual" stroke="#ea580c" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="anterior" stroke="#0f766e" strokeWidth={2} dot={false} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : null}
    </article>
  );
}

function formatOffset(seconds: number): string {
  if (seconds < 3600) {
    return `${Math.round(seconds / 60)}m`;
  }
  return `${(seconds / 3600).toFixed(1)}h`;
}
