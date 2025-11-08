from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.services.trading_service import TradingService
from app.repositories.decision_repo import DecisionRepository

router = APIRouter(tags=["trade"])


@router.post("/trade/decide")
def trade_decide(payload: dict, session: Session = Depends(db_session)) -> dict:
    symbol = payload.get("symbol")
    granularity = payload.get("granularity", "daily")
    cash = float(payload.get("cash", 0))
    svc = TradingService()
    decision = svc.decide(symbol, granularity, cash)
    # persist decision
    DecisionRepository().insert(
        session,
        symbol=symbol,
        action=decision["action"],
        quantity=decision["quantity"],
        confidence=decision["confidence"],
        reason=decision["reason"],
    )
    return {"decision": decision, "explain": svc.explain()}


