import json
from typing import Any

from openai import OpenAI

from app.core.config import Settings
from app.schemas.chat import ChatMessage, ChatRequest, ChatResponse, ChatSuggestionsResponse, ToolCallTrace
from app.schemas.filters import AnalyticsFilters
from app.services.analytics_service import AnalyticsService


class ChatService:
    def __init__(self, analytics_service: AnalyticsService, settings: Settings) -> None:
        self.analytics_service = analytics_service
        self.settings = settings

    def answer(self, request: ChatRequest) -> ChatResponse:
        filters = request.filters or AnalyticsFilters()
        if not self.settings.openai_api_key:
            return self._local_answer(request, filters)

        tool_calls: list[ToolCallTrace] = []
        client = OpenAI(api_key=self.settings.openai_api_key)
        messages = self._build_messages(request.history, request.message, filters)

        first = client.chat.completions.create(
            model=self.settings.resolved_model_name,
            messages=messages,
            tools=self._tools(),
            tool_choice="auto",
        )
        assistant_message = first.choices[0].message
        messages.append(assistant_message.model_dump(exclude_none=True))

        for call in assistant_message.tool_calls or []:
            arguments = self._parse_arguments(call.function.arguments)
            result = self._run_tool(call.function.name, arguments, filters)
            tool_calls.append(ToolCallTrace(name=call.function.name, arguments=arguments))
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, default=str),
                }
            )

        if not tool_calls:
            result = self._run_tool("get_kpis", {}, filters)
            tool_calls.append(ToolCallTrace(name="get_kpis", arguments={}))
            messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": "forced_get_kpis",
                            "type": "function",
                            "function": {"name": "get_kpis", "arguments": "{}"},
                        }
                    ],
                }
            )
            messages.append({"role": "tool", "tool_call_id": "forced_get_kpis", "content": json.dumps(result, default=str)})

        final = client.chat.completions.create(
            model=self.settings.resolved_model_name,
            messages=[
                *messages,
                {
                    "role": "system",
                    "content": (
                        "Answer using only facts returned by tools. If the tools do not contain a requested number, "
                        "say that the data is not available. Keep the answer concise and cite the relevant metric names."
                    ),
                },
            ],
        )
        answer = final.choices[0].message.content or "I could not generate an answer from the available tool results."
        return ChatResponse(answer=answer, used_ai=True, tool_calls=tool_calls)

    def suggestions(self) -> ChatSuggestionsResponse:
        return ChatSuggestionsResponse(
            suggestions=[
                "¿A qué hora hubo más tiendas visibles en el período seleccionado?",
                "¿Cuánto tiempo estuvo la disponibilidad por debajo del umbral?",
                "¿Hubo caídas bruscas durante la tarde?",
                "¿Cuál fue el promedio de tiendas visibles entre estas horas?",
                "¿Alguna ventana parece un ramp-up del sistema?",
            ]
        )

    def _local_answer(self, request: ChatRequest, filters: AnalyticsFilters) -> ChatResponse:
        lower_message = request.message.lower()
        if "unstable" in lower_message or "ranking" in lower_message or "top" in lower_message:
            result = self._run_tool("get_top_unstable_stores", {"limit": 5}, filters)
            first = result["items"][0] if result["items"] else None
            answer = (
                "OpenAI is not configured yet, so I used backend tools directly. "
                f"The most unstable source window is {first['entity_label']} with volatility "
                f"{self._format_number(first['stddev_visible_stores'])}."
                if first
                else "OpenAI is not configured yet, and no unstable source windows matched the filters."
            )
            return ChatResponse(answer=answer, used_ai=False, tool_calls=[ToolCallTrace(name="get_top_unstable_stores", arguments={"limit": 5})])

        result = self._run_tool("get_kpis", {}, filters)
        answer = (
            "OpenAI is not configured yet, so I used backend tools directly. "
            f"Current visible stores are {self._format_number(result['current_visible_stores'])}, "
            f"latest delta is {self._format_number(result['delta_visible_stores'])}, "
            f"and the selected range has {self._format_number(result['points_count'])} points."
        )
        return ChatResponse(answer=answer, used_ai=False, tool_calls=[ToolCallTrace(name="get_kpis", arguments={})])

    def _run_tool(self, name: str, arguments: dict[str, Any], request_filters: AnalyticsFilters) -> dict[str, Any]:
        filters = self._merge_filters(request_filters, arguments.get("filters"))
        if name == "get_kpis":
            return self.analytics_service.get_kpis(filters).model_dump(mode="json")
        if name == "get_availability_trend":
            filters.granularity = arguments.get("granularity") or filters.granularity
            filters.limit = self._bounded_int(arguments.get("limit"), default=120, minimum=1, maximum=500)
            return self.analytics_service.get_availability_trend(filters).model_dump(mode="json")
        if name == "get_top_unstable_stores":
            filters.limit = self._bounded_int(arguments.get("limit"), default=10, minimum=1, maximum=50)
            return self.analytics_service.get_top_unstable_stores(filters).model_dump(mode="json")
        if name == "get_distribution":
            filters.bucket_count = self._bounded_int(arguments.get("bucket_count"), default=20, minimum=2, maximum=50)
            return self.analytics_service.get_distribution(filters).model_dump(mode="json")
        if name == "get_delta_trend":
            filters.granularity = arguments.get("granularity") or filters.granularity
            filters.limit = self._bounded_int(arguments.get("limit"), default=240, minimum=1, maximum=1000)
            return self.analytics_service.get_delta_trend(filters).model_dump(mode="json")
        if name == "get_hourly_heatmap":
            return self.analytics_service.get_hourly_heatmap(filters).model_dump(mode="json")
        if name == "get_period_comparison":
            filters.limit = self._bounded_int(arguments.get("limit"), default=500, minimum=1, maximum=1000)
            return self.analytics_service.get_period_comparison(filters).model_dump(mode="json")
        if name == "get_monitoring_windows":
            filters.limit = self._bounded_int(arguments.get("limit"), default=20, minimum=1, maximum=100)
            return self.analytics_service.get_monitoring_windows(filters).model_dump(mode="json")
        if name == "get_stores_table":
            pagination = arguments.get("pagination") if isinstance(arguments.get("pagination"), dict) else {}
            sorting = arguments.get("sorting") if isinstance(arguments.get("sorting"), dict) else {}
            filters.limit = self._bounded_int(pagination.get("limit"), default=10, minimum=1, maximum=100)
            filters.offset = self._bounded_int(pagination.get("offset"), default=0, minimum=0, maximum=5000)
            if sorting.get("sort_by"):
                filters.sort_by = sorting["sort_by"]
            if sorting.get("sort_direction"):
                filters.sort_direction = sorting["sort_direction"]
            return self.analytics_service.get_stores_table(filters).model_dump(mode="json")
        if name == "describe_schema":
            options = self.analytics_service.get_filter_options()
            return {
                "tables": ["availability_points", "availability_enriched", "load_metadata"],
                "grain": "CSV files are wide monitoring exports. Backend ingestion transposes timestamp columns into one row per timestamp, metric, and monitoring window.",
                "native_granularity": "10 seconds",
                "store_grain_note": "The current dataset has no individual store_id dimension; source_file is a monitoring-window proxy, not an individual store.",
                "metrics": options.metrics,
                "granularities": options.granularities,
                "min_timestamp": options.min_timestamp.isoformat() if options.min_timestamp else None,
                "max_timestamp": options.max_timestamp.isoformat() if options.max_timestamp else None,
            }
        return {"error": f"Unsupported tool: {name}"}

    def _merge_filters(self, base: AnalyticsFilters, raw_filters: Any) -> AnalyticsFilters:
        data = base.model_dump()
        if isinstance(raw_filters, dict):
            for key in [
                "start",
                "end",
                "metric",
                "source_file",
                "source_files",
                "granularity",
                "hour_from",
                "hour_to",
                "threshold_min",
                "compare_previous",
                "anomaly_drop_pct",
                "y_scale",
                "limit",
                "offset",
                "sort_by",
                "sort_direction",
                "bucket_count",
            ]:
                if raw_filters.get(key) is not None:
                    data[key] = raw_filters[key]
        return AnalyticsFilters(**data)

    def _build_messages(self, history: list[ChatMessage], message: str, filters: AnalyticsFilters) -> list[dict[str, Any]]:
        return [
            {
                "role": "system",
                "content": (
                    "You are a semantic analytics assistant for an AI-Powered Dashboard. "
                    "You must use tools for factual answers. Do not invent figures. "
                    "The frontend never calls OpenAI; all tools run in the backend. "
                    "The metric synthetic_monitoring_visible_stores is a synthetic monitoring time series of visible stores. "
                    "CSV timestamp columns are observations at native 10-second granularity. "
                    "Important: the current dataset does not include individual stores; source_file/source windows are monitoring windows, not stores."
                ),
            },
            {
                "role": "system",
                "content": f"Active dashboard filters: {filters.model_dump(mode='json')}",
            },
            *({"role": item.role, "content": item.content} for item in history[-8:]),
            {"role": "user", "content": message},
        ]

    def _tools(self) -> list[dict[str, Any]]:
        filter_schema = {
            "type": "object",
            "properties": {
                "start": {"type": "string", "description": "ISO datetime"},
                "end": {"type": "string", "description": "ISO datetime"},
                "metric": {"type": "string"},
                "source_file": {"type": "string"},
                "source_files": {"type": "array", "items": {"type": "string"}},
                "hour_from": {"type": "integer", "minimum": 0, "maximum": 23},
                "hour_to": {"type": "integer", "minimum": 0, "maximum": 23},
                "threshold_min": {"type": "number"},
                "anomaly_drop_pct": {"type": "number"},
            },
            "additionalProperties": False,
        }
        return [
            self._tool("get_kpis", "Get official KPI metrics for the selected filters.", {"filters": filter_schema}),
            self._tool(
                "get_availability_trend",
                "Get official availability trend points.",
                {
                    "filters": filter_schema,
                    "granularity": {"type": "string", "enum": ["raw", "10s", "1min", "5min", "15min", "1h", "hour", "day"]},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 500},
                },
            ),
            self._tool(
                "get_delta_trend",
                "Get official delta points and anomaly flags for visible stores.",
                {
                    "filters": filter_schema,
                    "granularity": {"type": "string", "enum": ["raw", "10s", "1min", "5min", "15min", "1h", "hour", "day"]},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 1000},
                },
            ),
            self._tool("get_hourly_heatmap", "Get official hourly/day pattern cells.", {"filters": filter_schema}),
            self._tool(
                "get_period_comparison",
                "Compare current selected period against the immediately previous period.",
                {"filters": filter_schema, "limit": {"type": "integer", "minimum": 1, "maximum": 1000}},
            ),
            self._tool(
                "get_top_unstable_stores",
                "Rank source windows by instability. In this dataset source windows proxy stores.",
                {"filters": filter_schema, "limit": {"type": "integer", "minimum": 1, "maximum": 50}},
            ),
            self._tool(
                "get_distribution",
                "Get official distribution buckets for visible stores.",
                {
                    "filters": filter_schema,
                    "group_by": {"type": "string", "enum": ["visible_stores"]},
                    "metric": {"type": "string"},
                    "bucket_count": {"type": "integer", "minimum": 2, "maximum": 50},
                },
            ),
            self._tool(
                "get_stores_table",
                "Get paginated source-window table. In this dataset source windows proxy stores.",
                {
                    "filters": filter_schema,
                    "pagination": {
                        "type": "object",
                        "properties": {"limit": {"type": "integer"}, "offset": {"type": "integer"}},
                        "additionalProperties": False,
                    },
                    "sorting": {
                        "type": "object",
                        "properties": {
                            "sort_by": {
                                "type": "string",
                                "enum": [
                                    "entity_label",
                                    "avg_visible_stores",
                                    "min_visible_stores",
                                    "max_visible_stores",
                                    "stddev_visible_stores",
                                    "range_visible_stores",
                                    "points_count",
                                    "min_timestamp",
                                    "max_timestamp",
                                ],
                            },
                            "sort_direction": {"type": "string", "enum": ["asc", "desc"]},
                        },
                        "additionalProperties": False,
                    },
                },
            ),
            self._tool(
                "get_monitoring_windows",
                "Get monitoring-window metadata, behavior classification, and statistics by source file.",
                {"filters": filter_schema, "limit": {"type": "integer", "minimum": 1, "maximum": 100}},
            ),
            self._tool("describe_schema", "Describe available analytical schema, grain, and limitations.", {}),
        ]

    def _tool(self, name: str, description: str, properties: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {"type": "object", "properties": properties, "additionalProperties": False},
            },
        }

    def _parse_arguments(self, raw_arguments: str | None) -> dict[str, Any]:
        if not raw_arguments:
            return {}
        try:
            parsed = json.loads(raw_arguments)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _bounded_int(self, value: Any, default: int, minimum: int, maximum: int) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = default
        return max(min(parsed, maximum), minimum)

    def _format_number(self, value: float | int | None) -> str:
        if value is None:
            return "not available"
        return f"{round(value):,}"
