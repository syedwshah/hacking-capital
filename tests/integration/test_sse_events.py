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


