from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck_connects_to_duckdb() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["duckdb_connected"] is True


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


def test_chat_uses_analytics_fallback_without_openai_key() -> None:
    response = client.post("/chat", json={"message": "What is the current availability?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["used_ai"] is False
    assert payload["tool_calls"][0]["name"] == "get_availability_summary"
