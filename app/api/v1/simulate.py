from fastapi import APIRouter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
import json
import time
from datetime import datetime
from typing import List
from app.api.deps import db_session
from app.services.trading_service import TradingService
from app.services.data_service import DataService
from app.repositories.trade_repo import TradeRepository
from app.repositories.decision_repo import DecisionRepository
from app.core.cache import KnowledgeCache

router = APIRouter(tags=["simulate"])


@router.post("/simulate/stream")
def simulate_stream(payload: dict) -> dict:
    # Placeholder: would stream events; for now return stub
    return {"events": []}


@router.get("/simulate/events")
def simulate_events(symbol: str, steps: int = 10, cash: float = 1000.0, session: Session = Depends(db_session)):
    svc = TradingService()
    trade_repo = TradeRepository()
    decision_repo = DecisionRepository()
    prices = DataService().fetch(symbol, "2020-01-01", "2020-01-31", "1m")
    prices = prices[-steps:] if len(prices) >= steps else prices

    def event_generator():
        nonlocal cash
        for i, bar in enumerate(prices, start=1):
            d = svc.decide(symbol, "1m", cash)
            # simple paper trade: buy uses all cash at last price; sell closes position (stubbed qty)
            qty = d["quantity"]
            event = {"step": i, "symbol": symbol, "ts": bar["ts"], "price": bar["close"], "decision": d, "explain": svc.explain()}

            # Persist every decision to Decision table for comprehensive tracking
            decision_repo.insert(
                session,
                symbol=symbol,
                action=d["action"],
                quantity=d["quantity"],
                confidence=d["confidence"],
                reason=d["reason"]
            )

            # Persist trades for BUY/SELL actions to Trade table
            if d["action"] in {"BUY", "SELL"}:
                trade_repo.insert(session, symbol=symbol, action=d["action"], price=bar["close"], quantity=qty, fees=0.0)

            yield {"event": "trade", "data": json.dumps(event)}
            time.sleep(0.2)

    return EventSourceResponse(event_generator())


@router.post("/simulate/batch")
def simulate_batch(payload: dict, session: Session = Depends(db_session)) -> dict:
    symbols: List[str] = payload.get("symbols", [])
    steps = int(payload.get("steps", 10))
    cash = float(payload.get("cash", 1000.0))
    if not symbols:
        return {"results": []}

    results = []
    svc = TradingService()
    cache = KnowledgeCache()
    decision_repo = DecisionRepository()
    trade_repo = TradeRepository()

    for symbol in symbols:
        # Generate consistent synthetic data for batch simulation (same as live trading)
        import random
        base_price = 150.0

        # Create trending data with consistent seed for reproducibility
        random.seed(hash(symbol) % 10000)  # Consistent seed per symbol
        trend_type = random.choice(["up", "down", "sideways"])
        trend_strength = random.uniform(2, 8) if trend_type != "sideways" else 0

        prices = []
        for i in range(max(steps, 5)):  # Ensure at least 5 points for trend analysis
            if trend_type == "up":
                price_change = trend_strength * (i / 4) + random.uniform(-1, 3)
            elif trend_type == "down":
                price_change = -trend_strength * (i / 4) + random.uniform(-3, 1)
            else:
                price_change = random.uniform(-2, 2)

            close_price = base_price + price_change
            prices.append({
                "close": round(close_price, 2),
                "ts": f"2024-01-01T10:{i:02d}:00",
                "symbol": symbol
            })

        prices = prices[-steps:] if len(prices) >= steps else prices
        decisions = []
        explain_totals = []

        for bar in prices:
            d = svc.decide(symbol, "1m", cash)
            decisions.append(d)
            explain = svc.explain()
            explain_totals.append(explain.get("combined_score", 0.0))

            # Persist every decision to Decision table for comprehensive tracking
            decision_repo.insert(
                session,
                symbol=symbol,
                action=d["action"],
                quantity=d["quantity"],
                confidence=d["confidence"],
                reason=d["reason"]
            )

            # Persist trades for BUY/SELL actions to Trade table
            if d["action"] in {"BUY", "SELL"}:
                trade_repo.insert(
                    session,
                    symbol=symbol,
                    action=d["action"],
                    price=bar["close"],
                    quantity=d["quantity"],
                    fees=0.0
                )

        cache_hit = cache.get_summary(symbol, "1m") is not None
        actions = [d["action"] for d in decisions]

        # Store synthetic market data for reuse
        synthetic_data_key = f"synthetic_data_{symbol}_1m"
        cache.set_summary(symbol, "1m", {
            "synthetic_data": prices,
            "trend_type": trend_type,
            "trend_strength": trend_strength,
            "generated_at": datetime.now().isoformat()
        }, ttl_s=3600)  # Cache for 1 hour

        results.append(
            {
                "symbol": symbol,
                "steps": len(decisions),
                "actions": actions,
                "avg_confidence": sum(d["confidence"] for d in decisions) / len(decisions) if decisions else 0.0,
                "avg_score": sum(explain_totals) / len(explain_totals) if explain_totals else 0.0,
                "cache_hit": cache_hit,
                "synthetic_data": prices,  # Include synthetic data in response
                "trend_info": {
                    "type": trend_type,
                    "strength": trend_strength
                }
            }
        )

    return {"results": results}


@router.get("/simulate/history")
def get_simulation_history(limit: int = 20, session: Session = Depends(db_session)) -> dict:
    """Get recent simulation history and batch processing results."""
    decision_repo = DecisionRepository()

    # Get recent decisions (last 24 hours for simulations)
    recent_decisions = decision_repo.list_recent(session, limit=limit * 10)  # Get more to filter

    # Group by time windows to identify simulation batches
    from collections import defaultdict
    import datetime

    # Group decisions into potential simulation batches (decisions within 2-minute windows)
    simulation_batches = defaultdict(list)

    for decision in recent_decisions:
        # Round timestamp to nearest 2-minute window for better batch grouping
        # This helps group decisions that happen close together in batch simulations
        minutes = decision.ts.minute
        rounded_minutes = (minutes // 2) * 2  # Round down to nearest 2-minute boundary
        batch_key = decision.ts.replace(minute=rounded_minutes, second=0, microsecond=0)
        simulation_batches[batch_key].append({
            "id": decision.id,
            "symbol": decision.symbol,
            "timestamp": decision.ts.isoformat(),
            "action": decision.action,
            "quantity": decision.quantity,
            "confidence": decision.confidence,
            "reason": decision.reason
        })

    # Convert to list and sort by time
    batch_list = []
    for batch_time, decisions in simulation_batches.items():
        # Consider batches with 2+ decisions or high-frequency decisions
        if len(decisions) >= 2:
            batch_list.append({
                "batch_id": f"batch_{batch_time.strftime('%Y%m%d_%H%M')}",
                "batch_timestamp": batch_time.isoformat(),
                "decision_count": len(decisions),
                "symbols": list(set(d["symbol"] for d in decisions)),
                "symbol_count": len(set(d["symbol"] for d in decisions)),
                "actions": [d["action"] for d in decisions],
                "avg_confidence": sum(d["confidence"] for d in decisions) / len(decisions),
                "decisions": decisions[:15]  # Show more decisions per batch
            })

    # Sort by most recent first
    batch_list.sort(key=lambda x: x["batch_timestamp"], reverse=True)

    # Limit results
    batch_list = batch_list[:limit]

    return {
        "simulation_batches": batch_list,
        "total_batches": len(batch_list),
        "total_decisions": sum(batch["decision_count"] for batch in batch_list)
    }


