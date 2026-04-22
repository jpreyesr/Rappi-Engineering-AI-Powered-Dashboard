import { BarChart3 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatCompactNumber, formatNumber, formatPercent } from "../../../lib/formatters";
import type { DistributionResponse } from "../types";
import { EmptyState, LoadingBlock } from "./StateBlocks";

type DistributionChartProps = {
  distribution: DistributionResponse | null;
  isLoading: boolean;
};

export function DistributionChart({ distribution, isLoading }: DistributionChartProps) {
  const data = (distribution?.buckets ?? []).map((bucket) => ({
    label: `${formatCompactNumber(bucket.bucket_start)}-${formatCompactNumber(bucket.bucket_end)}`,
    count: bucket.count,
    percentage: bucket.percentage,
  }));

  return (
    <article className="rounded-lg border p-4">
      <div className="mb-4 flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-orange-600" aria-hidden="true" />
        <div>
          <h2 className="text-lg font-semibold text-slate-950">Distribución de tiendas visibles</h2>
          <p className="mt-1 text-sm text-slate-500">Cuánto tiempo estuvo la plataforma en cada rango de disponibilidad.</p>
        </div>
      </div>

      {isLoading && data.length === 0 ? <LoadingBlock className="h-[320px]" /> : null}
      {!isLoading && data.length === 0 ? (
        <EmptyState title="Sin distribución" description="Ningún punto coincide con los filtros activos." />
      ) : null}
      {data.length > 0 ? (
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 10, right: 16, bottom: 42, left: 0 }}>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" vertical={false} />
              <XAxis dataKey="label" angle={-25} textAnchor="end" interval={0} tick={{ fontSize: 11, fill: "#525252" }} />
              <YAxis tickFormatter={formatCompactNumber} width={64} tick={{ fontSize: 12, fill: "#525252" }} />
              <Tooltip
                formatter={(value: unknown, name: unknown, item: unknown) => {
                  const payload = (item as { payload?: { percentage?: number } }).payload;
                  return [`${formatNumber(Number(value))} (${formatPercent(payload?.percentage ?? null)})`, "Lecturas"];
                }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {distribution?.buckets.map((bucket) => (
                  <Cell key={bucket.bucket_index} fill={bucket.contains_latest ? "#ea580c" : "#334155"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : null}
    </article>
  );
}
