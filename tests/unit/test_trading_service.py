from app.services.trading_service import TradingService


def test_decide_stub():
    svc = TradingService()
    d = svc.decide("AAPL", "daily", 1000.0)
    assert d["action"] in {"BUY", "HOLD", "SELL"}
    assert "confidence" in d

