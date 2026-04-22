import { ChatPanel } from "../features/chat/components/ChatPanel";
import { DashboardHeader } from "../features/dashboard/components/DashboardHeader";
import { DeltaTrendChart } from "../features/dashboard/components/DeltaTrendChart";
import { DistributionChart } from "../features/dashboard/components/DistributionChart";
import { ErrorBanner } from "../features/dashboard/components/StateBlocks";
import { FilterBar } from "../features/dashboard/components/FilterBar";
import { HourlyHeatmap } from "../features/dashboard/components/HourlyHeatmap";
import { KpiCards } from "../features/dashboard/components/KpiCards";
import { PeriodComparisonChart } from "../features/dashboard/components/PeriodComparisonChart";
import { StoresTable } from "../features/dashboard/components/StoresTable";
import { TrendChart } from "../features/dashboard/components/TrendChart";
import { UnstableRankingChart } from "../features/dashboard/components/UnstableRankingChart";
import { useDashboardData } from "../features/dashboard/hooks/useDashboardData";

export function DashboardPage() {
  const dashboard = useDashboardData();

  return (
    <main className="min-h-screen bg-neutral-100 text-neutral-950">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <DashboardHeader
          options={dashboard.options}
          kpis={dashboard.kpis}
          sourcesCount={dashboard.sources?.total}
          isLoading={dashboard.isLoading}
        />
        <ErrorBanner message={dashboard.error} />
        <FilterBar
          filters={dashboard.filters}
          options={dashboard.options}
          isLoading={dashboard.isLoadingOptions}
          onChange={dashboard.updateFilters}
          onReset={dashboard.resetFilters}
        />
        <KpiCards kpis={dashboard.kpis} isLoading={dashboard.isLoadingData} />

        <section className="grid gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(360px,0.9fr)]">
          <TrendChart
            trend={dashboard.trend}
            isLoading={dashboard.isLoadingData}
            yScale={dashboard.filters.yScale}
            recommendedYScale={dashboard.kpis?.recommended_y_scale}
          />
          <UnstableRankingChart unstable={dashboard.unstable} isLoading={dashboard.isLoadingData} />
        </section>

        <section className="grid gap-6 xl:grid-cols-2">
          <DeltaTrendChart deltaTrend={dashboard.deltaTrend} isLoading={dashboard.isLoadingData} />
          <PeriodComparisonChart comparison={dashboard.comparison} isLoading={dashboard.isLoadingData} />
        </section>

        <section className="grid gap-6 xl:grid-cols-[minmax(360px,0.85fr)_minmax(0,1.2fr)]">
          <DistributionChart distribution={dashboard.distribution} isLoading={dashboard.isLoadingData} />
          <HourlyHeatmap heatmap={dashboard.heatmap} isLoading={dashboard.isLoadingData} />
        </section>

        <section>
          <StoresTable
            table={dashboard.storesTable}
            tableState={dashboard.tableState}
            isLoading={dashboard.isLoadingData}
            onPageChange={dashboard.setTablePage}
            onSortChange={dashboard.setTableSort}
          />
        </section>

        <ChatPanel filters={dashboard.analyticsFilters} />
      </div>
    </main>
  );
}
