import { LineChart } from "lucide-react";
import {
  CartesianGrid,
  Line,
  LineChart as RechartsLineChart,
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
};

export function TrendChart({ trend, isLoading }: TrendChartProps) {
  const chartData = toAvailabilityChartData(trend?.points ?? []);

  return (
    <article className="rounded-md border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <LineChart className="h-5 w-5 text-emerald-700" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-neutral-950">Availability Trend</h2>
          </div>
          <p className="mt-1 text-sm text-neutral-500">Backend aggregate by {trend?.granularity ?? "hour"}</p>
        </div>
        <p className="text-sm text-neutral-500">
          {chartData.length > 0
            ? `${formatDateTime(chartData[0].timestamp)} - ${formatDateTime(chartData[chartData.length - 1].timestamp)}`
            : "No range"}
        </p>
      </div>

      {isLoading && chartData.length === 0 ? <LoadingBlock className="h-[380px]" /> : null}
      {!isLoading && chartData.length === 0 ? (
        <EmptyState title="No trend data" description="Try widening the date range or clearing the source filter." />
      ) : null}
      {chartData.length > 0 ? (
        <div className="h-[380px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RechartsLineChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" />
              <XAxis dataKey="label" minTickGap={28} tick={{ fontSize: 12, fill: "#525252" }} />
              <YAxis tickFormatter={formatCompactNumber} width={72} tick={{ fontSize: 12, fill: "#525252" }} />
              <Tooltip
                formatter={(value: unknown, name: unknown) => [
                  formatNumber(Number(value)),
                  name === "deltaVisibleStores" ? "Delta" : "Visible stores",
                ]}
                labelClassName="text-sm font-medium text-neutral-700"
              />
              <Line
                type="monotone"
                dataKey="visibleStores"
                stroke="#047857"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="deltaVisibleStores"
                stroke="#2563eb"
                strokeWidth={1.5}
                dot={false}
              />
            </RechartsLineChart>
          </ResponsiveContainer>
        </div>
      ) : null}
    </article>
  );
}
