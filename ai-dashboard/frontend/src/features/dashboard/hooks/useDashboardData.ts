import { useEffect, useMemo, useState } from "react";

import {
  getAnalyticsKpis,
  getAvailabilityTrend,
  getDataSources,
  getDeltaTrend,
  getDistribution,
  getFilterOptions,
  getHourlyHeatmap,
  getPeriodComparison,
  getStoresTable,
  getTopUnstableStores,
} from "../../../services/analytics";
import type {
  AnalyticsFilters,
  AnalyticsKpisResponse,
  AvailabilityTrendResponse,
  DataSourcesResponse,
  DeltaTrendResponse,
  DistributionResponse,
  FilterOptionsResponse,
  Granularity,
  HourlyHeatmapResponse,
  PeriodComparisonResponse,
  StoresTableResponse,
  StoresTableSortBy,
  TopUnstableStoresResponse,
} from "../types";

type DashboardFilterState = {
  startDate: string;
  endDate: string;
  metric: string;
  sourceFiles: string[];
  granularity: Granularity;
  hourFrom: string;
  hourTo: string;
  thresholdMin: string;
  comparePrevious: boolean;
  anomalyDropPct: string;
  yScale: "auto" | "linear" | "log";
};

type TableState = {
  page: number;
  pageSize: number;
  sortBy: StoresTableSortBy;
  sortDirection: "asc" | "desc";
};

const DEFAULT_FILTERS: DashboardFilterState = {
  startDate: "",
  endDate: "",
  metric: "",
  sourceFiles: [],
  granularity: "1h",
  hourFrom: "",
  hourTo: "",
  thresholdMin: "",
  comparePrevious: false,
  anomalyDropPct: "5",
  yScale: "auto",
};

const DEFAULT_TABLE: TableState = {
  page: 0,
  pageSize: 10,
  sortBy: "stddev_visible_stores",
  sortDirection: "desc",
};

export function useDashboardData() {
  const [options, setOptions] = useState<FilterOptionsResponse | null>(null);
  const [filters, setFilters] = useState<DashboardFilterState>(DEFAULT_FILTERS);
  const [tableState, setTableState] = useState<TableState>(DEFAULT_TABLE);
  const [kpis, setKpis] = useState<AnalyticsKpisResponse | null>(null);
  const [trend, setTrend] = useState<AvailabilityTrendResponse | null>(null);
  const [deltaTrend, setDeltaTrend] = useState<DeltaTrendResponse | null>(null);
  const [unstable, setUnstable] = useState<TopUnstableStoresResponse | null>(null);
  const [distribution, setDistribution] = useState<DistributionResponse | null>(null);
  const [heatmap, setHeatmap] = useState<HourlyHeatmapResponse | null>(null);
  const [comparison, setComparison] = useState<PeriodComparisonResponse | null>(null);
  const [storesTable, setStoresTable] = useState<StoresTableResponse | null>(null);
  const [sources, setSources] = useState<DataSourcesResponse | null>(null);
  const [isLoadingOptions, setIsLoadingOptions] = useState(true);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadOptions() {
      try {
        const response = await getFilterOptions();
        setOptions(response);
        setFilters((current) => ({
          ...current,
          metric: current.metric || response.metrics[0] || "",
          startDate: current.startDate || toDateInput(response.min_timestamp),
          endDate: current.endDate || toDateInput(response.max_timestamp),
        }));
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Unable to load filter options.");
      } finally {
        setIsLoadingOptions(false);
      }
    }

    void loadOptions();
  }, []);

  const analyticsFilters = useMemo(
    () =>
      buildAnalyticsFilters(filters, {
        limit: 500,
      }),
    [filters],
  );

  useEffect(() => {
    if (!options) {
      return;
    }

    async function loadDashboard() {
      setIsLoadingData(true);
      setError(null);
      try {
        const tableFilters = buildAnalyticsFilters(filters, {
          limit: tableState.pageSize,
          offset: tableState.page * tableState.pageSize,
          sort_by: tableState.sortBy,
          sort_direction: tableState.sortDirection,
        });
        const [
          kpisResponse,
          trendResponse,
          deltaResponse,
          unstableResponse,
          distributionResponse,
          heatmapResponse,
          comparisonResponse,
          tableResponse,
          sourcesResponse,
        ] = await Promise.all([
          getAnalyticsKpis(analyticsFilters),
          getAvailabilityTrend(analyticsFilters),
          getDeltaTrend(analyticsFilters),
          getTopUnstableStores({ ...analyticsFilters, limit: 8 }),
          getDistribution({ ...analyticsFilters, bucket_count: 12 }),
          getHourlyHeatmap(analyticsFilters),
          getPeriodComparison({ ...analyticsFilters, compare_previous: true }),
          getStoresTable(tableFilters),
          getDataSources(),
        ]);
        setKpis(kpisResponse);
        setTrend(trendResponse);
        setDeltaTrend(deltaResponse);
        setUnstable(unstableResponse);
        setDistribution(distributionResponse);
        setHeatmap(heatmapResponse);
        setComparison(comparisonResponse);
        setStoresTable(tableResponse);
        setSources(sourcesResponse);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Unable to load dashboard data.");
      } finally {
        setIsLoadingData(false);
      }
    }

    void loadDashboard();
  }, [analyticsFilters, filters, options, tableState]);

  function updateFilters(next: Partial<DashboardFilterState>) {
    setFilters((current) => ({ ...current, ...next }));
    setTableState((current) => ({ ...current, page: 0 }));
  }

  function resetFilters() {
    setFilters({
      ...DEFAULT_FILTERS,
      metric: options?.metrics[0] || "",
      startDate: toDateInput(options?.min_timestamp ?? null),
      endDate: toDateInput(options?.max_timestamp ?? null),
    });
    setTableState(DEFAULT_TABLE);
  }

  function setTablePage(page: number) {
    setTableState((current) => ({ ...current, page: Math.max(page, 0) }));
  }

  function setTableSort(sortBy: StoresTableSortBy) {
    setTableState((current) => ({
      ...current,
      page: 0,
      sortBy,
      sortDirection: current.sortBy === sortBy && current.sortDirection === "desc" ? "asc" : "desc",
    }));
  }

  return {
    options,
    filters,
    analyticsFilters,
    tableState,
    kpis,
    trend,
    deltaTrend,
    unstable,
    distribution,
    heatmap,
    comparison,
    storesTable,
    sources,
    isLoading: isLoadingOptions || isLoadingData,
    isLoadingOptions,
    isLoadingData,
    error,
    updateFilters,
    resetFilters,
    setTablePage,
    setTableSort,
  };
}

function buildAnalyticsFilters(
  filters: DashboardFilterState,
  overrides: Partial<AnalyticsFilters>,
): AnalyticsFilters {
  return {
    start: filters.startDate ? `${filters.startDate}T00:00:00` : null,
    end: filters.endDate ? `${filters.endDate}T23:59:59` : null,
    metric: filters.metric || null,
    source_file: filters.sourceFiles.length === 1 ? filters.sourceFiles[0] : null,
    source_files: filters.sourceFiles,
    granularity: filters.granularity,
    hour_from: filters.hourFrom ? Number(filters.hourFrom) : null,
    hour_to: filters.hourTo ? Number(filters.hourTo) : null,
    threshold_min: filters.thresholdMin ? Number(filters.thresholdMin) : null,
    compare_previous: filters.comparePrevious,
    anomaly_drop_pct: filters.anomalyDropPct ? Number(filters.anomalyDropPct) : 5,
    y_scale: filters.yScale,
    ...overrides,
  };
}

function toDateInput(value: string | null): string {
  return value ? value.slice(0, 10) : "";
}
