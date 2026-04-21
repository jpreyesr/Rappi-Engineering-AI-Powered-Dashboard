import json
from typing import Any

from openai import OpenAI

from app.core.config import Settings
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse, ToolCallTrace
from app.services.analytics_service import AnalyticsService


class ChatService:
    def __init__(self, analytics_service: AnalyticsService, settings: Settings) -> None:
        self.analytics_service = analytics_service
        self.settings = settings

    def answer(self, request: ChatRequest) -> ChatResponse:
        if not self.settings.openai_api_key:
            return self._local_answer(request)

        tool_calls: list[ToolCallTrace] = []
        client = OpenAI(api_key=self.settings.openai_api_key)
        messages = self._build_messages(request.history, request.message)
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_availability_summary",
                    "description": "Return current KPIs and dataset coverage for store availability data.",
                    "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
                },
            }
        ]

        first = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        choice = first.choices[0].message
        messages.append(choice.model_dump(exclude_none=True))

        for call in choice.tool_calls or []:
            if call.function.name != "get_availability_summary":
                continue
            arguments = json.loads(call.function.arguments or "{}")
            result = self.analytics_service.compact_context()
            tool_calls.append(ToolCallTrace(name=call.function.name, arguments=arguments))
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, default=str),
                }
            )

        if tool_calls:
            final = client.chat.completions.create(
                model=self.settings.openai_model,
                messages=messages,
            )
            answer = final.choices[0].message.content or "I could not generate an answer."
        else:
            answer = choice.content or "I could not generate an answer."

        return ChatResponse(answer=answer, used_ai=True, tool_calls=tool_calls)

    def _local_answer(self, request: ChatRequest) -> ChatResponse:
        context = self.analytics_service.compact_context()
        answer = (
            "OpenAI is not configured yet, so I answered from the backend analytics layer. "
            f"The dataset has {context['points_count']:,} points across {context['files_count']} files. "
            f"The latest visible store count is {self._format_number(context['current_visible_stores'])}, "
            f"with an average of {self._format_number(context['average_visible_stores'])} over the available range. "
            f"The data runs from {context['min_timestamp']} to {context['max_timestamp']}."
        )
        return ChatResponse(
            answer=answer,
            used_ai=False,
            tool_calls=[ToolCallTrace(name="get_availability_summary", arguments={})],
        )

    def _build_messages(self, history: list[ChatMessage], message: str) -> list[dict[str, Any]]:
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    "You are an analytics assistant for a local AI-Powered Dashboard. "
                    "Use the provided tool for availability metrics. Be concise, factual, "
                    "and do not invent data that is not returned by tools."
                ),
            }
        ]
        messages.extend({"role": item.role, "content": item.content} for item in history[-8:])
        messages.append({"role": "user", "content": message})
        return messages

    def _format_number(self, value: float | int | None) -> str:
        if value is None:
            return "not available"
        return f"{round(value):,}"
