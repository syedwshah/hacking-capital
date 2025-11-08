from fastapi import APIRouter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
import json
import time
from app.api.deps import db_session
from app.services.trading_service import TradingService
from app.services.data_service import DataService
from app.repositories.trade_repo import TradeRepository

router = APIRouter(tags=["simulate"])


@router.post("/simulate/stream")
def simulate_stream(payload: dict) -> dict:
    # Placeholder: would stream events; for now return stub
    return {"events": []}


@router.get("/simulate/events")
def simulate_events(symbol: str, steps: int = 10, cash: float = 1000.0, session: Session = Depends(db_session)):
    svc = TradingService()
    repo = TradeRepository()
    prices = DataService().fetch(symbol, "2020-01-01", "2020-01-31", "1m")
    prices = prices[-steps:] if len(prices) >= steps else prices

    def event_generator():
        nonlocal cash
        for i, bar in enumerate(prices, start=1):
            d = svc.decide(symbol, "1m", cash)
            # simple paper trade: buy uses all cash at last price; sell closes position (stubbed qty)
            qty = d["quantity"]
            event = {"step": i, "symbol": symbol, "ts": bar["ts"], "price": bar["close"], "decision": d, "explain": svc.explain()}
            # persist trade if action is BUY or SELL
            if d["action"] in {"BUY", "SELL"}:
                repo.insert(session, symbol=symbol, action=d["action"], price=bar["close"], quantity=qty, fees=0.0)
            yield {"event": "trade", "data": json.dumps(event)}
            time.sleep(0.2)

    return EventSourceResponse(event_generator())


