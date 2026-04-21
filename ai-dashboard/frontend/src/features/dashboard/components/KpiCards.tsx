import { Activity, Gauge, Sigma, TrendingUp } from "lucide-react";

import { formatNumber } from "../../../lib/formatters";
import type { AnalyticsKpisResponse } from "../types";
import { LoadingBlock } from "./StateBlocks";

type KpiCardsProps = {
  kpis: AnalyticsKpisResponse | null;
  isLoading: boolean;
};

const cards = [
  { key: "current_visible_stores", label: "Current visible stores", helper: "Latest backend point", icon: Activity },
  { key: "average_visible_stores", label: "Average visible stores", helper: "Selected range average", icon: Sigma },
  { key: "delta_visible_stores", label: "Latest delta", helper: "Versus previous point", icon: TrendingUp },
  { key: "volatility_visible_stores", label: "Volatility", helper: "Standard deviation", icon: Gauge },
] as const;

export function KpiCards({ kpis, isLoading }: KpiCardsProps) {
  if (isLoading && !kpis) {
    return (
      <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {cards.map((card) => (
          <LoadingBlock key={card.key} className="h-32" />
        ))}
      </section>
    );
  }

  return (
    <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <article key={card.key} className="rounded-md border border-neutral-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-medium text-neutral-600">{card.label}</p>
              <Icon className="h-4 w-4 shrink-0 text-emerald-700" aria-hidden="true" />
            </div>
            <p className="mt-3 text-3xl font-semibold text-neutral-950">{formatNumber(kpis?.[card.key] ?? null)}</p>
            <p className="mt-1 min-h-5 text-xs text-neutral-500">{card.helper}</p>
          </article>
        );
      })}
    </section>
  );
}
