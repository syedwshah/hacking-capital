from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from app.api.deps import db_session
from app.services.trading_service import TradingService
from app.repositories.decision_repo import DecisionRepository
from app.repositories.trade_repo import TradeRepository

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


@router.get("/trade/history")
def get_trading_history(
    symbol: Optional[str] = None,
    limit: int = 50,
    session: Session = Depends(db_session)
) -> Dict[str, Any]:
    """Get trading decision history."""
    decisions = DecisionRepository().list_recent(session, symbol=symbol, limit=limit)

    # Convert to serializable format
    history = []
    for decision in decisions:
        history.append({
            "id": decision.id,
            "symbol": decision.symbol,
            "timestamp": decision.ts.isoformat(),
            "action": decision.action,
            "quantity": decision.quantity,
            "confidence": decision.confidence,
            "reason": decision.reason
        })

    # Calculate basic stats
    total_decisions = len(history)
    buy_decisions = len([d for d in history if d["action"] == "BUY"])
    sell_decisions = len([d for d in history if d["action"] == "SELL"])
    avg_confidence = sum(d["confidence"] for d in history) / total_decisions if total_decisions > 0 else 0

    return {
        "history": history,
        "stats": {
            "total_decisions": total_decisions,
            "buy_decisions": buy_decisions,
            "sell_decisions": sell_decisions,
            "hold_decisions": total_decisions - buy_decisions - sell_decisions,
            "avg_confidence": avg_confidence
        }
    }


@router.get("/trade/performance")
def get_trading_performance(
    symbol: Optional[str] = None,
    days: int = 30,
    session: Session = Depends(db_session)
) -> Dict[str, Any]:
    """Get trading performance metrics."""
    from datetime import datetime, timedelta

    # Get decisions from the last N days
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    decisions = DecisionRepository().list_after_date(session, cutoff_date, symbol=symbol)

    if not decisions:
        return {"performance": {}, "message": "No trading data available"}

    # Calculate performance metrics
    total_decisions = len(decisions)
    buy_decisions = len([d for d in decisions if d.action == "BUY"])
    sell_decisions = len([d for d in decisions if d.action == "SELL"])

    confidence_levels = [d.confidence for d in decisions]
    avg_confidence = sum(confidence_levels) / len(confidence_levels) if confidence_levels else 0

    # Mock performance calculation (in real implementation, this would track actual P&L)
    win_rate = sum(1 for d in decisions if d.confidence > 0.6) / total_decisions if total_decisions > 0 else 0

    performance = {
        "total_decisions": total_decisions,
        "buy_decisions": buy_decisions,
        "sell_decisions": sell_decisions,
        "avg_confidence": avg_confidence,
        "win_rate": win_rate,
        "high_confidence_trades": len([d for d in decisions if d.confidence > 0.8]),
        "period_days": days
    }

    return {"performance": performance}


