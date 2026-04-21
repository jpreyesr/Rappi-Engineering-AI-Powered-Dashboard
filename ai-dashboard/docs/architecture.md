# AI-Powered Dashboard Architecture

This project is a local modular monolith.

## Ownership Boundaries

- Backend owns data access, DuckDB, ingestion, analytics, and chatbot tool execution.
- Frontend owns UI, user interaction, chart rendering, and API calls.
- Dashboard and chat must use the same backend analytics service.
- React must not duplicate analytical aggregation logic that already exists in FastAPI.

## Current Backend Flow

FastAPI routes call services. Services call repositories. Repositories query DuckDB through a small client.

`/analytics/summary` and `/analytics/timeseries` are the dashboard-facing analytical APIs. `/chat` uses the same analytics service through OpenAI tool calling when `OPENAI_API_KEY` is configured, and falls back to a local analytics answer when it is not.

## Current Data Source

The first executable version reads `data/processed/dashboard.duckdb` in read-only mode. Full ingestion from CSV remains a later phase.
