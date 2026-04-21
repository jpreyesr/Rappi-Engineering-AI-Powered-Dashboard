import type { AnalyticsFilters, ChatMessage, ChatResponse, ChatSuggestionsResponse } from "../types/api";
import { apiGet, apiPost } from "./api";

export function getChatSuggestions(): Promise<ChatSuggestionsResponse> {
  return apiGet<ChatSuggestionsResponse>("/api/chat/suggestions");
}

export function sendChatMessage(
  message: string,
  history: ChatMessage[],
  filters?: AnalyticsFilters,
): Promise<ChatResponse> {
  return apiPost<ChatResponse, { message: string; history: ChatMessage[]; filters?: AnalyticsFilters }>("/api/chat", {
    message,
    history,
    filters,
  });
}
