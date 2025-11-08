from app.main import app
from fastapi.testclient import TestClient


def test_sse_events_streams_some_data():
    client = TestClient(app)
    with client.stream("GET", "/api/v1/simulate/events?symbol=AAPL&steps=3&cash=1000") as r:
        assert r.status_code == 200
        text_chunks = []
        for chunk in r.iter_text():
            text_chunks.append(chunk)
            if len(text_chunks) >= 1:
                break
        assert any("data:" in c or "{\"step\":" in c for c in text_chunks)


def test_simulate_batch_returns_results():
    client = TestClient(app)
    payload = {"symbols": ["AAPL", "MSFT"], "steps": 5, "cash": 1000}
    r = client.post("/api/v1/simulate/batch", json=payload)
    assert r.status_code == 200
    result = r.json()
    assert "results" in result
    assert len(result["results"]) == 2
    for item in result["results"]:
        assert "symbol" in item
        assert "steps" in item
        assert "actions" in item
        assert "avg_confidence" in item
        assert "avg_score" in item
        assert "cache_hit" in item


