import { useEffect, useState } from "react";

import { getChatSuggestions, sendChatMessage } from "../../../services/chat";
import type { AnalyticsFilters } from "../../../types/api";
import type { ChatMessage } from "../types";

export function useAnalyticsChat(filters: AnalyticsFilters) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [draft, setDraft] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadSuggestions() {
      try {
        const response = await getChatSuggestions();
        setSuggestions(response.suggestions);
        setDraft(response.suggestions[0] ?? "");
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : "Unable to load chat suggestions.");
      }
    }

    void loadSuggestions();
  }, []);

  async function send(messageOverride?: string) {
    const message = (messageOverride ?? draft).trim();
    if (!message || isLoading) {
      return;
    }

    const nextMessages: ChatMessage[] = [...messages, { role: "user", content: message }];
    setMessages(nextMessages);
    setDraft("");
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(message, messages.slice(-8), filters);
      setMessages([...nextMessages, { role: "assistant", content: response.answer }]);
    } catch (caught) {
      const content = caught instanceof Error ? caught.message : "Unable to reach the chat endpoint.";
      setError(content);
      setMessages([...nextMessages, { role: "assistant", content }]);
    } finally {
      setIsLoading(false);
    }
  }

  function clear() {
    setMessages([]);
    setError(null);
  }

  return {
    messages,
    suggestions,
    draft,
    isLoading,
    error,
    setDraft,
    send,
    clear,
  };
}
