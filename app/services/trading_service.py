from __future__ import annotations

from app.schemas.trade import TradeDecision
from app.services.data_service import DataService
from app.services.metrics import simple_moving_average, rsi, macd
from app.core.cache import KnowledgeCache
from app.db.base import get_session
from app.repositories.agent_repo import AgentWeightRepository


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

        # RSI and MACD
        rsi_vals = rsi(closes, 14)
        last_rsi = rsi_vals[-1]
        macd_line, signal_line, hist = macd(closes)
        last_hist = hist[-1] if hist else 0.0

        # Rule blend
        weights = self._load_weights()
        score = 0.0
        # SMA crossover
        sma_score = 0.5 if last_fast > last_slow * 1.001 else (-0.5 if last_fast < last_slow * 0.999 else 0.0)
        score += sma_score * weights.get("primary", 0.5)
        # RSI momentum
        rsi_score = 0.0
        if last_rsi > 55:
            rsi_score = min(0.3, (last_rsi - 55) / 100)
        elif last_rsi < 45:
            rsi_score = -min(0.3, (45 - last_rsi) / 100)
        score += rsi_score * weights.get("investor_patterns", 0.25)
        # MACD histogram
        macd_score = max(-0.2, min(0.2, last_hist / 10.0))
        score += macd_score * weights.get("sentiment_tailwinds", 0.25)

        action = "HOLD"
        if score > 0.1:
            action = "BUY"
        elif score < -0.1:
            action = "SELL"

        qty = 0
        if action == "BUY" and last_price > 0:
            qty = round(cash / last_price, 4)
        confidence = min(1.0, abs(score))  # scaled 0..1
        reason = f"sma10={last_fast:.2f}, sma20={last_slow:.2f}, rsi14={last_rsi:.1f}, macd_hist={last_hist:.4f}, score={score:.3f}, price={last_price:.2f}"
        if cache_payload:
            reason = f"{reason}; cache=hit"
        else:
            reason = f"{reason}; cache=miss"

        decision = TradeDecision(action=action, quantity=qty, confidence=confidence, reason=reason)
        self._explain = [
            {"agent": "primary", "score": sma_score, "weight": weights.get("primary", 0.5), "reason": "SMA crossover"},
            {"agent": "investor_patterns", "score": rsi_score, "weight": weights.get("investor_patterns", 0.25), "reason": f"RSI {last_rsi:.1f}"},
            {"agent": "sentiment_tailwinds", "score": macd_score, "weight": weights.get("sentiment_tailwinds", 0.25), "reason": f"MACD hist {last_hist:.4f}"},
        ]
        self._explain_total = score
        return decision.model_dump()

    def explain(self) -> list[dict]:
        data = getattr(self, "_explain", [])
        total = getattr(self, "_explain_total", 0.0)
        return {"agents": data, "combined_score": total}

    def _load_weights(self) -> dict[str, float]:
        with get_session() as session:
            weights = AgentWeightRepository().get_all(session)
        if not weights:
            return {"primary": 0.5, "investor_patterns": 0.25, "sentiment_tailwinds": 0.25}
        return {item["agent"]: float(item["weight"]) for item in weights}


