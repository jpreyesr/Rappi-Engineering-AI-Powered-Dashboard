import { LineChart } from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { toAvailabilityChartData } from "../../../lib/chartHelpers";
import { formatCompactNumber, formatDateTime, formatNumber } from "../../../lib/formatters";
import type { AvailabilityTrendResponse } from "../types";
import { EmptyState, LoadingBlock } from "./StateBlocks";

type TrendChartProps = {
  trend: AvailabilityTrendResponse | null;
  isLoading: boolean;
  yScale: "auto" | "linear" | "log";
  recommendedYScale?: string;
};

export function TrendChart({ trend, isLoading, yScale, recommendedYScale }: TrendChartProps) {
  const chartData = toAvailabilityChartData(trend?.points ?? []);
  const effectiveScale = yScale === "auto" ? recommendedYScale ?? "linear" : yScale;

  return (
    <article className="rounded-md border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <LineChart className="h-5 w-5 text-emerald-700" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-neutral-950">Tiendas visibles en el tiempo</h2>
          </div>
          <p className="mt-1 text-sm text-neutral-500">
            Agregado por {trend?.granularity ?? "1h"} · escala {effectiveScale === "log" ? "logarítmica" : "lineal"}
          </p>
        </div>
        <p className="text-sm text-neutral-500">
          {chartData.length > 0
            ? `${formatDateTime(chartData[0].timestamp)} - ${formatDateTime(chartData[chartData.length - 1].timestamp)}`
            : "No range"}
        </p>
      </div>

      {isLoading && chartData.length === 0 ? <LoadingBlock className="h-[380px]" /> : null}
      {!isLoading && chartData.length === 0 ? (
        <EmptyState title="Sin tendencia" description="Amplía el rango o limpia el filtro de ventana." />
      ) : null}
      {chartData.length > 0 ? (
        <div className="h-[380px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" />
              <XAxis dataKey="label" minTickGap={28} tick={{ fontSize: 12, fill: "#525252" }} />
              <YAxis
                tickFormatter={formatCompactNumber}
                width={72}
                tick={{ fontSize: 12, fill: "#525252" }}
                scale={effectiveScale === "log" ? "log" : "auto"}
                domain={effectiveScale === "log" ? ["auto", "auto"] : undefined}
              />
              <Tooltip
                formatter={(value: unknown, name: unknown) => [
                  formatNumber(Number(value)),
                  name === "deltaVisibleStores" ? "Delta" : "Visible stores",
                ]}
                labelClassName="text-sm font-medium text-neutral-700"
              />
              {chartData[0]?.p50VisibleStores ? <ReferenceLine y={chartData[0].p50VisibleStores} stroke="#64748b" strokeDasharray="4 4" /> : null}
              {chartData[0]?.p95VisibleStores ? <ReferenceLine y={chartData[0].p95VisibleStores} stroke="#7c3aed" strokeDasharray="4 4" /> : null}
              <Area
                type="monotone"
                dataKey="visibleStores"
                stroke="#047857"
                fill="#a7f3d0"
                fillOpacity={0.45}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      ) : null}
    </article>
  );
}
