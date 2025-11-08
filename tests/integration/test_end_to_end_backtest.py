def test_backtest_stub(client):
    r = client.post("/api/v1/backtest/run", json={"symbol": "AAPL", "start_date": "2020-01-01", "end_date": "2020-12-31", "initial_cash": 1000})
    assert r.status_code == 200
    result = r.json()
    assert "final_cash" in result
    assert "final_equity" in result
    assert "trades" in result
    assert "snapshots" in result
    assert "max_drawdown" in result
    assert "strategy_return" in result
    assert "buy_hold_return" in result
    assert "total_fees" in result
    assert "summary" in result


