from __future__ import annotations

from app.schemas.trade import TradeDecision
from app.services.data_service import DataService
from app.services.technical_indicators import TechnicalIndicators, IndicatorResult
from app.core.cache import KnowledgeCache
from app.db.base import get_session
from app.repositories.agent_repo import AgentWeightRepository
from app.vectorstore.sqlite_json import SqliteJsonVectorStore
import datetime
import random
import openai
import os


class TradingService:
    def decide(self, symbol: str, granularity: str, cash: float) -> dict:
        # Fetch market data using OpenAI web crawling
        interval = "1m" if granularity in {"minute", "1m"} else "daily"
        rows = DataService().fetch(symbol, "2020-01-01", "2020-01-31", interval)

        if len(rows) < 5:  # Minimum data for LLM analysis
            decision = TradeDecision(action="HOLD", quantity=0, confidence=0.5, reason="insufficient-data")
            return decision.model_dump()

        # Use OpenAI for LLM-powered trading decision
        return self._llm_decide(symbol, rows, cash)

    def _llm_decide(self, symbol: str, market_data: list, cash: float) -> dict:
        """Use OpenAI GPT for LLM-powered trading decisions"""
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            # Fallback to simple random decision if no OpenAI key
            action = random.choice(["BUY", "SELL", "HOLD"])
            confidence = random.uniform(0.3, 0.8)
            reason = f"LLM unavailable - random decision: {action}"
            quantity = 1 if action != "HOLD" else 0

            decision = TradeDecision(action=action, quantity=quantity, confidence=confidence, reason=reason)
            return decision.model_dump()

        try:
            client = openai.OpenAI(api_key=openai_key)

            # Prepare market data summary for LLM
            recent_data = market_data[-10:]  # Last 10 data points
            prices = [f"{d['close']:.2f}" for d in recent_data]
            volumes = [str(d.get('volume', 1000)) for d in recent_data]

            prompt = f"""
            You are an expert quantitative trader analyzing {symbol} stock data.

            Recent price data (last 10 periods): {', '.join(prices)}
            Recent volume data: {', '.join(volumes)}
            Current cash available: ${cash:.2f}

            Based on this market data, make a trading decision. Consider:
            - Price trends and momentum
            - Volume patterns
            - Risk management (don't risk more than 10% of cash per trade)
            - Market conditions and volatility

            Respond with ONLY a JSON object in this exact format:
            {{
                "action": "BUY" or "SELL" or "HOLD",
                "quantity": number (0 if HOLD, or shares to buy/sell),
                "confidence": number between 0.1 and 1.0,
                "reason": "brief explanation of your decision"
            }}
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )

            content = response.choices[0].message.content.strip()

            # Try to parse JSON response
            try:
                import json
                decision_data = json.loads(content)

                # Validate and sanitize the response
                action = decision_data.get("action", "HOLD").upper()
                if action not in ["BUY", "SELL", "HOLD"]:
                    action = "HOLD"

                quantity = max(0, int(decision_data.get("quantity", 0)))
                confidence = max(0.1, min(1.0, float(decision_data.get("confidence", 0.5))))
                reason = decision_data.get("reason", f"LLM decision: {action}")

                decision = TradeDecision(action=action, quantity=quantity, confidence=confidence, reason=reason)
                return decision.model_dump()

            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Failed to parse LLM response: {e}")
                print(f"LLM response: {content}")

        except Exception as e:
            print(f"LLM decision failed: {e}")

        # Final fallback
        decision = TradeDecision(action="HOLD", quantity=0, confidence=0.5, reason="LLM service unavailable")
        return decision.model_dump()

    def explain(self) -> list[dict]:
        # For LLM-based decisions, provide simple explanation
        return {"agents": [{"agent": "llm_trader", "reason": "GPT-powered trading decision"}], "combined_score": 0.0}

