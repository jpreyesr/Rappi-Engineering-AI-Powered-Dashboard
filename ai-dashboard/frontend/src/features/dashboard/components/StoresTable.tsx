import { ArrowDown, ArrowUp, ChevronLeft, ChevronRight } from "lucide-react";

import { formatDateTime, formatNumber } from "../../../lib/formatters";
import type { StoresTableResponse, StoresTableSortBy } from "../types";
import { EmptyState, LoadingBlock } from "./StateBlocks";

type TableState = {
  page: number;
  pageSize: number;
  sortBy: StoresTableSortBy;
  sortDirection: "asc" | "desc";
};

type StoresTableProps = {
  table: StoresTableResponse | null;
  tableState: TableState;
  isLoading: boolean;
  onPageChange: (page: number) => void;
  onSortChange: (sortBy: StoresTableSortBy) => void;
};

const columns: Array<{ key: StoresTableSortBy; label: string; align?: "right" }> = [
  { key: "entity_label", label: "Source window" },
  { key: "avg_visible_stores", label: "Avg", align: "right" },
  { key: "min_visible_stores", label: "Min", align: "right" },
  { key: "max_visible_stores", label: "Max", align: "right" },
  { key: "stddev_visible_stores", label: "Volatility", align: "right" },
  { key: "points_count", label: "Points", align: "right" },
  { key: "min_timestamp", label: "Start" },
  { key: "max_timestamp", label: "End" },
];

export function StoresTable({ table, tableState, isLoading, onPageChange, onSortChange }: StoresTableProps) {
  const rows = table?.rows ?? [];
  const total = table?.total ?? 0;
  const pageCount = Math.max(Math.ceil(total / tableState.pageSize), 1);

  return (
    <article className="rounded-md border border-neutral-200 bg-white shadow-sm">
      <div className="flex flex-col gap-2 border-b border-neutral-200 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-neutral-950">Source Windows Table</h2>
          <p className="mt-1 text-sm text-neutral-500">Paginated backend rows by source window.</p>
        </div>
        <p className="text-sm text-neutral-500">{formatNumber(total)} rows</p>
      </div>

      {isLoading && rows.length === 0 ? <div className="p-4"><LoadingBlock className="h-72" /></div> : null}
      {!isLoading && rows.length === 0 ? (
        <div className="p-4">
          <EmptyState title="No table rows" description="Try clearing filters or choosing a wider date range." />
        </div>
      ) : null}
      {rows.length > 0 ? (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full border-collapse text-sm">
              <thead className="bg-neutral-50 text-left text-xs font-semibold uppercase tracking-normal text-neutral-500">
                <tr>
                  {columns.map((column) => (
                    <th key={column.key} className={column.align === "right" ? "px-4 py-3 text-right" : "px-4 py-3"}>
                      <button
                        type="button"
                        onClick={() => onSortChange(column.key)}
                        className={
                          column.align === "right"
                            ? "ml-auto inline-flex items-center gap-1 text-right"
                            : "inline-flex items-center gap-1"
                        }
                      >
                        {column.label}
                        {tableState.sortBy === column.key ? (
                          tableState.sortDirection === "asc" ? (
                            <ArrowUp className="h-3.5 w-3.5" aria-hidden="true" />
                          ) : (
                            <ArrowDown className="h-3.5 w-3.5" aria-hidden="true" />
                          )
                        ) : null}
                      </button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {rows.map((row) => (
                  <tr key={row.entity_id} className="hover:bg-neutral-50">
                    <td className="max-w-[280px] truncate px-4 py-3 font-medium text-neutral-800" title={row.entity_label}>
                      {row.entity_label}
                    </td>
                    <td className="px-4 py-3 text-right text-neutral-700">{formatNumber(row.avg_visible_stores)}</td>
                    <td className="px-4 py-3 text-right text-neutral-700">{formatNumber(row.min_visible_stores)}</td>
                    <td className="px-4 py-3 text-right text-neutral-700">{formatNumber(row.max_visible_stores)}</td>
                    <td className="px-4 py-3 text-right text-neutral-700">{formatNumber(row.stddev_visible_stores)}</td>
                    <td className="px-4 py-3 text-right text-neutral-700">{formatNumber(row.points_count)}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-neutral-700">{formatDateTime(row.min_timestamp)}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-neutral-700">{formatDateTime(row.max_timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between border-t border-neutral-200 px-4 py-3">
            <button
              type="button"
              onClick={() => onPageChange(tableState.page - 1)}
              disabled={tableState.page === 0 || isLoading}
              className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-neutral-300 text-neutral-700 transition hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-40"
              title="Previous page"
              aria-label="Previous page"
            >
              <ChevronLeft className="h-4 w-4" aria-hidden="true" />
            </button>
            <p className="text-sm text-neutral-600">
              Page {tableState.page + 1} of {pageCount}
            </p>
            <button
              type="button"
              onClick={() => onPageChange(tableState.page + 1)}
              disabled={tableState.page + 1 >= pageCount || isLoading}
              className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-neutral-300 text-neutral-700 transition hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-40"
              title="Next page"
              aria-label="Next page"
            >
              <ChevronRight className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </>
      ) : null}
    </article>
  );
}
