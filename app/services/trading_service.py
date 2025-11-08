from app.schemas.trade import TradeDecision


class TradingService:
    def decide(self, symbol: str, granularity: str, cash: float) -> dict:
        # Placeholder: deterministic fallback decision
        decision = TradeDecision(action="HOLD", quantity=0, confidence=0.5, reason="stub")
        return decision.model_dump()

    def explain(self) -> list[dict]:
        # Placeholder: per-agent contributions
        return []


