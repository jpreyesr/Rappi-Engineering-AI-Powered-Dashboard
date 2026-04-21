import { AlertTriangle } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { formatCompactNumber, formatNumber } from "../../../lib/formatters";
import type { TopUnstableStoresResponse } from "../types";
import { EmptyState, LoadingBlock } from "./StateBlocks";

type UnstableRankingChartProps = {
  unstable: TopUnstableStoresResponse | null;
  isLoading: boolean;
};

export function UnstableRankingChart({ unstable, isLoading }: UnstableRankingChartProps) {
  const data = (unstable?.items ?? []).map((item) => ({
    name: shortName(item.entity_label),
    volatility: item.stddev_visible_stores ?? 0,
    range: item.range_visible_stores ?? 0,
  }));

  return (
    <article className="rounded-md border border-neutral-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-amber-700" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-neutral-950">Most Unstable Sources</h2>
          </div>
          <p className="mt-1 text-sm text-neutral-500">Ranked by backend volatility. Source files stand in for stores.</p>
        </div>
      </div>

      {isLoading && data.length === 0 ? <LoadingBlock className="h-[320px]" /> : null}
      {!isLoading && data.length === 0 ? (
        <EmptyState title="No ranking data" description="No source windows matched the selected filters." />
      ) : null}
      {data.length > 0 ? (
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 84 }}>
              <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" horizontal={false} />
              <XAxis type="number" tickFormatter={formatCompactNumber} tick={{ fontSize: 12, fill: "#525252" }} />
              <YAxis type="category" dataKey="name" width={92} tick={{ fontSize: 12, fill: "#525252" }} />
              <Tooltip formatter={(value: unknown) => [formatNumber(Number(value)), "Volatility"]} />
              <Bar dataKey="volatility" fill="#d97706" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : null}
    </article>
  );
}

function shortName(value: string): string {
  return value.replace("AVAILABILITY-data ", "").replace("AVAILABILITY-data", "data");
}
