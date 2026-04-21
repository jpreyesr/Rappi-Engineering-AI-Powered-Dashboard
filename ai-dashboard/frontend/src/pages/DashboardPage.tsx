import { Bot, Database, LineChart, Loader2, Send, Store, TrendingUp } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart as RechartsLineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { toAvailabilityChartData } from "../lib/chartHelpers";
import { formatCompactNumber, formatDateTime, formatNumber } from "../lib/formatters";
import { getAvailabilitySummary, getAvailabilityTimeseries } from "../services/analytics";
import { sendChatMessage } from "../services/chat";
import type { AvailabilitySummary, ChatMessage, TimeSeriesResponse } from "../types/api";

type SubmitEvent = {
  preventDefault(): void;
};

export function DashboardPage() {
  const [summary, setSummary] = useState<AvailabilitySummary | null>(null);
  const [series, setSeries] = useState<TimeSeriesResponse | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("What is the current availability trend?");
  const [isLoading, setIsLoading] = useState(true);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setError(null);
        const [summaryResponse, seriesResponse] = await Promise.all([
          getAvailabilitySummary(),
          getAvailabilityTimeseries(),
        ]);
        setSummary(summaryResponse);
        setSeries(seriesResponse);
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Unable to load dashboard data.");
      } finally {
        setIsLoading(false);
      }
    }

    void loadDashboard();
  }, []);

  const chartData = useMemo(() => toAvailabilityChartData(series?.points ?? []), [series]);

  async function handleSend(event: SubmitEvent) {
    event.preventDefault();
    const message = draft.trim();
    if (!message || isChatLoading) {
      return;
    }

    const nextMessages: ChatMessage[] = [...messages, { role: "user", content: message }];
    setMessages(nextMessages);
    setDraft("");
    setIsChatLoading(true);

    try {
      const response = await sendChatMessage(message, messages);
      setMessages([...nextMessages, { role: "assistant", content: response.answer }]);
    } catch (caught) {
      const content = caught instanceof Error ? caught.message : "Unable to reach the chat endpoint.";
      setMessages([...nextMessages, { role: "assistant", content }]);
    } finally {
      setIsChatLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-neutral-100 text-neutral-950">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-4 border-b border-neutral-200 pb-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-medium text-emerald-700">Local analytics monolith</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-normal text-neutral-950">AI-Powered Dashboard</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-neutral-600">
              Store availability analytics served by FastAPI and DuckDB, with chat grounded in the same backend service.
            </p>
          </div>
          <div className="flex items-center gap-2 rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm text-neutral-700">
            <Database className="h-4 w-4 text-emerald-700" aria-hidden="true" />
            {summary ? `${formatNumber(summary.metadata.points_count)} points` : "Loading dataset"}
          </div>
        </header>

        {error ? (
          <section className="rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">{error}</section>
        ) : null}

        <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {(summary?.kpis ?? []).map((kpi) => (
            <article key={kpi.label} className="rounded-md border border-neutral-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm font-medium text-neutral-600">{kpi.label}</p>
                <Store className="h-4 w-4 shrink-0 text-emerald-700" aria-hidden="true" />
              </div>
              <p className="mt-3 text-3xl font-semibold text-neutral-950">{formatNumber(kpi.value)}</p>
              <p className="mt-1 min-h-5 text-xs text-neutral-500">{kpi.helper}</p>
            </article>
          ))}
          {isLoading
            ? Array.from({ length: 4 }).map((_, index) => (
                <article key={index} className="h-32 animate-pulse rounded-md border border-neutral-200 bg-white" />
              ))
            : null}
        </section>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
          <article className="rounded-md border border-neutral-200 bg-white p-4 shadow-sm">
            <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <LineChart className="h-5 w-5 text-emerald-700" aria-hidden="true" />
                  <h2 className="text-lg font-semibold text-neutral-950">Visible Stores Over Time</h2>
                </div>
                <p className="mt-1 text-sm text-neutral-500">
                  Hourly average from {formatDateTime(summary?.metadata.min_timestamp ?? null)} to{" "}
                  {formatDateTime(summary?.metadata.max_timestamp ?? null)}
                </p>
              </div>
              <div className="flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-sm text-amber-800">
                <TrendingUp className="h-4 w-4" aria-hidden="true" />
                Delta {formatNumber(summary?.delta_visible_stores ?? null)}
              </div>
            </div>

            <div className="h-[380px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <RechartsLineChart data={chartData} margin={{ top: 10, right: 20, bottom: 10, left: 0 }}>
                  <CartesianGrid stroke="#e5e7eb" strokeDasharray="4 4" />
                  <XAxis dataKey="label" minTickGap={28} tick={{ fontSize: 12, fill: "#525252" }} />
                  <YAxis
                    tickFormatter={formatCompactNumber}
                    width={72}
                    tick={{ fontSize: 12, fill: "#525252" }}
                  />
                  <Tooltip
                    formatter={(value: unknown) => [formatNumber(Number(value)), "Visible stores"]}
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
                </RechartsLineChart>
              </ResponsiveContainer>
            </div>
          </article>

          <aside className="flex min-h-[520px] flex-col rounded-md border border-neutral-200 bg-white shadow-sm">
            <div className="border-b border-neutral-200 p-4">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-emerald-700" aria-hidden="true" />
                <h2 className="text-lg font-semibold text-neutral-950">Analytics Chat</h2>
              </div>
              <p className="mt-1 text-sm text-neutral-500">Answers use the backend analytics service.</p>
            </div>

            <div className="flex-1 space-y-3 overflow-y-auto p-4">
              {messages.length === 0 ? (
                <p className="rounded-md bg-neutral-100 p-3 text-sm leading-6 text-neutral-600">
                  Ask about current availability, averages, dataset coverage, or latest changes.
                </p>
              ) : null}
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={
                    message.role === "user"
                      ? "ml-8 rounded-md bg-emerald-700 p-3 text-sm leading-6 text-white"
                      : "mr-8 rounded-md bg-neutral-100 p-3 text-sm leading-6 text-neutral-800"
                  }
                >
                  {message.content}
                </div>
              ))}
              {isChatLoading ? (
                <div className="mr-8 flex items-center gap-2 rounded-md bg-neutral-100 p-3 text-sm text-neutral-600">
                  <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
                  Thinking with backend data
                </div>
              ) : null}
            </div>

            <form onSubmit={handleSend} className="border-t border-neutral-200 p-3">
              <div className="flex gap-2">
                <input
                  value={draft}
                  onChange={(event: { target: { value: string } }) => setDraft(event.target.value)}
                  className="min-w-0 flex-1 rounded-md border border-neutral-300 px-3 py-2 text-sm outline-none transition focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
                  placeholder="Ask about availability"
                />
                <button
                  type="submit"
                  disabled={isChatLoading}
                  className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-emerald-700 text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
                  aria-label="Send message"
                  title="Send message"
                >
                  <Send className="h-4 w-4" aria-hidden="true" />
                </button>
              </div>
            </form>
          </aside>
        </section>
      </div>
    </main>
  );
}
