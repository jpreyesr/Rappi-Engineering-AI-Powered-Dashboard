import type { ChatMessage, ChatResponse } from "../types/api";
import { apiPost } from "./api";

export function sendChatMessage(message: string, history: ChatMessage[]): Promise<ChatResponse> {
  return apiPost<ChatResponse, { message: string; history: ChatMessage[] }>("/chat", {
    message,
    history,
  });
}
