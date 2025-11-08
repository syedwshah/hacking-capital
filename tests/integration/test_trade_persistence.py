from app.main import app
from fastapi.testclient import TestClient
from app.db.base import get_session
from app.repositories.decision_repo import DecisionRepository


def test_trade_decide_persists_decision():
    client = TestClient(app)
    symbol = "AAPL"
    r = client.post("/api/v1/trade/decide", json={"symbol": symbol, "granularity": "1m", "cash": 1000})
    assert r.status_code == 200
    with get_session() as session:
        items = DecisionRepository().list_for_symbol(session, symbol)
        assert isinstance(items, list)
        assert any(x["symbol"] == symbol for x in items)


