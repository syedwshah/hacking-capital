from __future__ import annotations

from app.schemas.trade import TradeDecision
from app.services.data_service import DataService
from app.services.metrics import simple_moving_average
from app.core.cache import KnowledgeCache


class TradingService:
    def decide(self, symbol: str, granularity: str, cash: float) -> dict:
        # Try cache first for summary-informed hints (not used deeply yet)
        cache_payload = KnowledgeCache().get_summary(symbol, granularity) or {}

        # Deterministic SMA crossover on recent synthetic data
        interval = "1m" if granularity in {"minute", "1m"} else "daily"
        rows = DataService().fetch(symbol, "2020-01-01", "2020-01-31", interval)
        closes = [r["close"] for r in rows][-200:]
        if len(closes) < 20:
            decision = TradeDecision(action="HOLD", quantity=0, confidence=0.5, reason="insufficient-data")
            self._explain = []
            return decision.model_dump()
        fast = simple_moving_average(closes, 10)
        slow = simple_moving_average(closes, 20)
        last_fast = fast[-1]
        last_slow = slow[-1]
        last_price = closes[-1]

        if last_fast > last_slow * 1.001:
            action = "BUY"
        elif last_fast < last_slow * 0.999:
            action = "SELL"
        else:
            action = "HOLD"

        qty = 0
        if action == "BUY" and last_price > 0:
            qty = round(cash / last_price, 4)
        confidence = min(1.0, abs(last_fast - last_slow) / max(1e-6, last_price))  # scaled
        reason = f"sma10={last_fast:.2f}, sma20={last_slow:.2f}, price={last_price:.2f}"
        if cache_payload:
            reason = f"{reason}; cache=hit"
        else:
            reason = f"{reason}; cache=miss"

        decision = TradeDecision(action=action, quantity=qty, confidence=confidence, reason=reason)
        self._explain = [
            {"agent": "deterministic_sma", "score": 1 if action == "BUY" else (-1 if action == "SELL" else 0), "confidence": confidence, "reason": reason}
        ]
        return decision.model_dump()

    def explain(self) -> list[dict]:
        return getattr(self, "_explain", [])


