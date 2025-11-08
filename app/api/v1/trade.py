from fastapi import APIRouter
from app.services.trading_service import TradingService

router = APIRouter(tags=["trade"])


@router.post("/trade/decide")
def trade_decide(payload: dict) -> dict:
    symbol = payload.get("symbol")
    granularity = payload.get("granularity", "daily")
    cash = float(payload.get("cash", 0))
    svc = TradingService()
    decision = svc.decide(symbol, granularity, cash)
    return {"decision": decision, "explain": svc.explain()}


