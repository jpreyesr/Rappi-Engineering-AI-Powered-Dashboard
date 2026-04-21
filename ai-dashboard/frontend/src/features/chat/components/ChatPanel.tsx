import { Bot, Loader2, Send, Trash2 } from "lucide-react";

import type { AnalyticsFilters } from "../../../types/api";
import { useAnalyticsChat } from "../hooks/useAnalyticsChat";

type SubmitEvent = {
  preventDefault(): void;
};

type ChatPanelProps = {
  filters: AnalyticsFilters;
};

export function ChatPanel({ filters }: ChatPanelProps) {
  const chat = useAnalyticsChat(filters);

  async function handleSubmit(event: SubmitEvent) {
    event.preventDefault();
    await chat.send();
  }

  return (
    <aside className="flex min-h-[560px] flex-col rounded-md border border-neutral-200 bg-white shadow-sm">
      <div className="flex items-start justify-between gap-3 border-b border-neutral-200 p-4">
        <div>
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-emerald-700" aria-hidden="true" />
            <h2 className="text-lg font-semibold text-neutral-950">Grounded Analytics Chat</h2>
          </div>
          <p className="mt-1 text-sm leading-6 text-neutral-500">
            Answers run through backend tools and use the active dashboard filters.
          </p>
        </div>
        <button
          type="button"
          onClick={chat.clear}
          className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-neutral-300 text-neutral-700 transition hover:bg-neutral-50"
          title="Clear chat"
          aria-label="Clear chat"
        >
          <Trash2 className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>

      <div className="border-b border-neutral-200 p-3">
        <div className="flex flex-wrap gap-2">
          {chat.suggestions.slice(0, 4).map((suggestion) => (
            <button
              key={suggestion}
              type="button"
              onClick={() => void chat.send(suggestion)}
              disabled={chat.isLoading}
              className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-left text-xs font-medium text-emerald-800 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {chat.messages.length === 0 ? (
          <div className="rounded-md bg-neutral-100 p-3 text-sm leading-6 text-neutral-600">
            Ask about KPIs, trends, instability, distributions, or source-window table rows. If the data is not in
            DuckDB, the assistant should say so.
          </div>
        ) : null}

        {chat.messages.map((message, index) => (
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

        {chat.isLoading ? (
          <div className="mr-8 flex items-center gap-2 rounded-md bg-neutral-100 p-3 text-sm text-neutral-600">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            Calling backend analytics tools
          </div>
        ) : null}

        {chat.error ? <p className="text-sm text-red-700">{chat.error}</p> : null}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-neutral-200 p-3">
        <div className="flex gap-2">
          <input
            value={chat.draft}
            onChange={(event: { target: { value: string } }) => chat.setDraft(event.target.value)}
            className="min-w-0 flex-1 rounded-md border border-neutral-300 px-3 py-2 text-sm outline-none transition focus:border-emerald-700 focus:ring-2 focus:ring-emerald-100"
            placeholder="Ask a grounded question"
          />
          <button
            type="submit"
            disabled={chat.isLoading}
            className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-emerald-700 text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
            title="Send message"
            aria-label="Send message"
          >
            <Send className="h-4 w-4" aria-hidden="true" />
          </button>
        </div>
      </form>
    </aside>
  );
}
