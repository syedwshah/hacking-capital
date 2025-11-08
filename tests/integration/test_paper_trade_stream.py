def test_simulate_stream_stub(client):
    r = client.post("/api/v1/simulate/stream", json={"symbol": "AAPL", "start_date": "2020-01-01", "end_date": "2020-02-01", "tick_interval": "1m", "mode": "synthetic_live"})
    assert r.status_code == 200
    assert "events" in r.json()


