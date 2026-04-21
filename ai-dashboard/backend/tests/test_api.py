from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck_connects_to_duckdb() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["duckdb_connected"] is True


def test_data_status_returns_current_load_state() -> None:
    response = client.get("/api/data/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in {"loaded", "not_loaded"}
    if payload["status"] == "loaded":
        assert payload["points_loaded"] > 0
        assert "availability_points" in payload["tables_created"]


def test_data_load_rebuilds_availability_tables() -> None:
    response = client.post("/api/data/load")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "loaded"
    assert payload["files_loaded"] > 0
    assert payload["points_loaded"] > 0
    assert "availability_points" in payload["tables_created"]
    assert "availability_enriched" in payload["tables_created"]


def test_summary_returns_dataset_kpis() -> None:
    response = client.get("/analytics/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["metadata"]["points_count"] > 0
    assert payload["current_visible_stores"] is not None
    assert len(payload["kpis"]) == 4


def test_timeseries_returns_points() -> None:
    response = client.get("/analytics/timeseries?granularity=hour&limit=10")

    assert response.status_code == 200
    payload = response.json()
    assert payload["granularity"] == "hour"
    assert 0 < len(payload["points"]) <= 10


def test_analytics_filter_options() -> None:
    response = client.get("/api/filters")

    assert response.status_code == 200
    payload = response.json()
    assert "synthetic_monitoring_visible_stores" in payload["metrics"]
    assert payload["min_timestamp"] is not None
    assert payload["max_timestamp"] is not None


def test_analytics_kpis_endpoint() -> None:
    response = client.post("/api/analytics/kpis", json={})

    assert response.status_code == 200
    payload = response.json()
    assert payload["points_count"] > 0
    assert payload["current_visible_stores"] is not None


def test_analytics_trend_endpoint() -> None:
    response = client.post("/api/analytics/availability-trend", json={"granularity": "hour", "limit": 5})

    assert response.status_code == 200
    payload = response.json()
    assert payload["granularity"] == "hour"
    assert 0 < len(payload["points"]) <= 5


def test_top_unstable_stores_uses_source_files_for_now() -> None:
    response = client.post("/api/analytics/top-unstable-stores", json={"limit": 3})

    assert response.status_code == 200
    payload = response.json()
    assert payload["entity_type"] == "source_file"
    assert 0 < len(payload["items"]) <= 3
    assert payload["items"][0]["entity_type"] == "source_file"


def test_distribution_endpoint_counts_filtered_points() -> None:
    response = client.post("/api/analytics/distribution", json={"bucket_count": 10})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_count"] > 0
    assert sum(bucket["count"] for bucket in payload["buckets"]) == payload["total_count"]


def test_stores_table_endpoint_is_paginated_by_source_file() -> None:
    response = client.post("/api/analytics/stores-table", json={"limit": 5, "offset": 0})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] > 0
    assert len(payload["rows"]) <= 5
    assert payload["rows"][0]["entity_type"] == "source_file"


def test_chat_uses_analytics_fallback_without_openai_key() -> None:
    response = client.post("/chat", json={"message": "What is the current availability?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["used_ai"] is False
    assert payload["tool_calls"][0]["name"] == "get_availability_summary"
