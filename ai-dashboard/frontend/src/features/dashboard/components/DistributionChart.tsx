import { BarChart3 } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
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
    <article className="rounded-md border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-center gap-2">
        <BarChart3 className="h-5 w-5 text-blue-700" aria-hidden="true" />
        <div>
          <h2 className="text-lg font-semibold text-neutral-950">Availability Distribution</h2>
          <p className="mt-1 text-sm text-neutral-500">Backend buckets by visible store count.</p>
        </div>
      </div>

      {isLoading && data.length === 0 ? <LoadingBlock className="h-[320px]" /> : null}
      {!isLoading && data.length === 0 ? (
        <EmptyState title="No distribution data" description="No points matched the selected filters." />
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
                  return [`${formatNumber(Number(value))} (${formatPercent(payload?.percentage ?? null)})`, "Points"];
                }}
              />
              <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : null}
    </article>
  );
}
