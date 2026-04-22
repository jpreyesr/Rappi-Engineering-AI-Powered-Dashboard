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
  { key: "entity_label", label: "Período" },
  { key: "avg_visible_stores", label: "Promedio", align: "right" },
  { key: "min_visible_stores", label: "Mínimo", align: "right" },
  { key: "max_visible_stores", label: "Máximo", align: "right" },
  { key: "stddev_visible_stores", label: "Variación", align: "right" },
  { key: "points_count", label: "Lecturas", align: "right" },
  { key: "min_timestamp", label: "Inicio" },
  { key: "max_timestamp", label: "Fin" },
];

export function StoresTable({ table, tableState, isLoading, onPageChange, onSortChange }: StoresTableProps) {
  const rows = table?.rows ?? [];
  const total = table?.total ?? 0;
  const pageCount = Math.max(Math.ceil(total / tableState.pageSize), 1);

  return (
    <article className="rounded-lg border">
      <div className="flex flex-col gap-2 border-b border-slate-200 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">Resumen por período observado</h2>
          <p className="mt-1 text-sm text-slate-500">Cada fila resume el conteo agregado de tiendas visibles en un archivo de observación.</p>
        </div>
        <p className="rounded-md bg-orange-50 px-2.5 py-1 text-sm font-medium text-orange-800">{formatNumber(total)} filas</p>
      </div>

      {isLoading && rows.length === 0 ? <div className="p-4"><LoadingBlock className="h-72" /></div> : null}
      {!isLoading && rows.length === 0 ? (
        <div className="p-4">
        <EmptyState title="Sin períodos" description="Limpia filtros o elige un rango más amplio." />
        </div>
      ) : null}
      {rows.length > 0 ? (
        <>
          <div className="overflow-x-auto">
            <table className="min-w-full border-collapse text-sm">
              <thead className="bg-slate-50 text-left text-xs font-semibold uppercase tracking-normal text-slate-500">
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
                  <th className="px-4 py-3">Comportamiento</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {rows.map((row) => (
                  <tr key={row.entity_id} className="hover:bg-orange-50">
                    <td className="max-w-[280px] truncate px-4 py-3 font-medium text-slate-800" title={row.entity_label}>
                      {row.entity_label}
                    </td>
                    <td className="px-4 py-3 text-right text-slate-700">{formatNumber(row.avg_visible_stores)}</td>
                    <td className="px-4 py-3 text-right text-slate-700">{formatNumber(row.min_visible_stores)}</td>
                    <td className="px-4 py-3 text-right text-slate-700">{formatNumber(row.max_visible_stores)}</td>
                    <td className="px-4 py-3 text-right text-slate-700">{formatNumber(row.stddev_visible_stores)}</td>
                    <td className="px-4 py-3 text-right text-slate-700">{formatNumber(row.points_count)}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-slate-700">{formatDateTime(row.min_timestamp)}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-slate-700">{formatDateTime(row.max_timestamp)}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-slate-700">{formatBehavior(row.behavior)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between border-t border-slate-200 px-4 py-3">
            <button
              type="button"
              onClick={() => onPageChange(tableState.page - 1)}
              disabled={tableState.page === 0 || isLoading}
              className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-300 text-slate-700 transition hover:bg-orange-50 disabled:cursor-not-allowed disabled:opacity-40"
              title="Página anterior"
              aria-label="Página anterior"
            >
              <ChevronLeft className="h-4 w-4" aria-hidden="true" />
            </button>
            <p className="text-sm text-slate-600">
              Página {tableState.page + 1} de {pageCount}
            </p>
            <button
              type="button"
              onClick={() => onPageChange(tableState.page + 1)}
              disabled={tableState.page + 1 >= pageCount || isLoading}
              className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-300 text-slate-700 transition hover:bg-orange-50 disabled:cursor-not-allowed disabled:opacity-40"
              title="Página siguiente"
              aria-label="Página siguiente"
            >
              <ChevronRight className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>
        </>
      ) : null}
    </article>
  );
}

function formatBehavior(value?: string | null): string {
  if (!value) {
    return "-";
  }
  if (value === "ramp_up") {
    return "ramp-up";
  }
  if (value === "stable") {
    return "estable";
  }
  if (value === "decreasing") {
    return "caída";
  }
  if (value === "oscillating") {
    return "oscilante";
  }
  return value;
}
