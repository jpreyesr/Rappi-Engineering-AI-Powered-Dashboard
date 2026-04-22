import { Activity, ArrowDownToLine, Clock, Gauge, Sigma, TrendingUp } from "lucide-react";

import { formatDuration, formatNumber, formatPercent } from "../../../lib/formatters";
import type { AnalyticsKpisResponse } from "../types";
import { LoadingBlock } from "./StateBlocks";

type KpiCardsProps = {
  kpis: AnalyticsKpisResponse | null;
  isLoading: boolean;
};

const cards = [
  { key: "current_visible_stores", label: "Última lectura", helper: "Último punto disponible", icon: Activity },
  { key: "average_visible_stores", label: "Promedio", helper: "Promedio del período", icon: Sigma },
  { key: "min_visible_stores", label: "Mínimo", helper: "Menor disponibilidad visible", icon: ArrowDownToLine },
  { key: "max_visible_stores", label: "Máximo", helper: "Pico del período", icon: TrendingUp },
  { key: "absolute_change_visible_stores", label: "Cambio absoluto", helper: "Fin menos inicio", icon: TrendingUp },
  { key: "percent_change_visible_stores", label: "Cambio porcentual", helper: "Variación inicio vs fin", icon: Gauge, percent: true },
  { key: "below_threshold_seconds", label: "Bajo umbral", helper: "Duración bajo el umbral activo", icon: Clock, duration: true },
  { key: "dominant_behavior", label: "Comportamiento", helper: "Clasificación por ventana", icon: Gauge },
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
          <article key={card.key} className="rounded-lg border p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-medium text-slate-600">{card.label}</p>
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-orange-50 text-orange-600">
                <Icon className="h-4 w-4 shrink-0" aria-hidden="true" />
              </span>
            </div>
            <p className="mt-3 text-3xl font-semibold text-slate-950">
              {"duration" in card
                ? formatDuration(Number(kpis?.[card.key] ?? 0))
                : "percent" in card
                  ? formatPercent(Number(kpis?.[card.key] ?? 0))
                  : formatNumber(kpis?.[card.key] ?? null)}
            </p>
            <p className="mt-1 min-h-5 text-xs text-slate-500">{card.helper}</p>
          </article>
        );
      })}
    </section>
  );
}
