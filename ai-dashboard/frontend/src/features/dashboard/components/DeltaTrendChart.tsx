import { Activity } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { formatCompactNumber, formatDateTime, formatNumber, formatPercent } from "../../../lib/formatters";
import type { DeltaTrendResponse } from "../types";
import { EmptyState, LoadingBlock } from "./StateBlocks";

type DeltaTrendChartProps = {
  deltaTrend: DeltaTrendResponse | null;
  isLoading: boolean;
};

export function DeltaTrendChart({ deltaTrend, isLoading }: DeltaTrendChartProps) {
  const data = (deltaTrend?.points ?? []).map((point) => ({
    label: formatDateTime(point.timestamp),
    timestamp: point.timestamp,
    delta: point.delta_visible_stores ?? 0,
    deltaPercent: point.delta_percent,
    isAnomaly: point.is_anomaly,
  }));

  return (
    <article className="rounded-lg border p-4">
      <div className="mb-4 flex items-center gap-2">
        <Activity className="h-5 w-5 text-orange-600" aria-hidden="true" />
        <div>
          <h2 className="text-lg font-semibold text-slate-950">Cambios en tiendas visibles</h2>
          <p className="mt-1 text-sm text-slate-500">
            Detecta caídas o recuperaciones del conteo; anomalía si cae más de {formatPercent(deltaTrend?.anomaly_drop_pct ?? null)}.
          </p>
        </div>
      </div>

      {isLoading && data.length === 0 ? <LoadingBlock className="h-[320px]" /> : null}
      {!isLoading && data.length === 0 ? (
        <EmptyState title="Sin delta" description="No hay puntos suficientes para calcular variación." />
      ) : null}
      {data.length > 0 ? (
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 16, bottom: 10, left: 0 }}>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" vertical={false} />
              <XAxis dataKey="label" minTickGap={28} tick={{ fontSize: 12, fill: "#525252" }} />
              <YAxis tickFormatter={formatCompactNumber} width={72} tick={{ fontSize: 12, fill: "#525252" }} />
              <Tooltip
                formatter={(value: unknown, _name: unknown, item: unknown) => {
                  const payload = (item as { payload?: { deltaPercent?: number | null } }).payload;
                  return [`${formatNumber(Number(value))} (${formatPercent(payload?.deltaPercent ?? null)})`, "Cambio de tiendas"];
                }}
              />
              <Bar dataKey="delta" radius={[3, 3, 0, 0]}>
                {data.map((entry) => (
                  <Cell key={`${entry.timestamp}-${entry.delta}`} fill={entry.isAnomaly ? "#dc2626" : entry.delta < 0 ? "#f97316" : "#0f766e"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : null}
    </article>
  );
}
