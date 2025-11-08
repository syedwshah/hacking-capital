def test_backtest_stub(client):
    r = client.post("/api/v1/backtest/run", json={"symbol": "AAPL", "start_date": "2020-01-01", "end_date": "2020-12-31", "initial_cash": 1000})
    assert r.status_code == 200
    assert "final_cash" in r.json()


