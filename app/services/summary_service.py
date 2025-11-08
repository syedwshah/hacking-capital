from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import json

from app.services.data_service import DataService
from app.vectorstore.sqlite_json import SqliteJsonVectorStore
import math

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class SummaryService:
    def __init__(self):
        self.openai_client = None
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _generate_openai_summary(self, symbol: str, period_data: List[dict], granularity: str) -> str:
        """Generate intelligent summary using OpenAI."""
        if not self.openai_client:
            return self._generate_basic_summary(symbol, period_data, granularity)

        # Prepare data for OpenAI
        prices = [item["close"] for item in period_data]
        volumes = [item.get("volume", 0) for item in period_data]

        # Calculate basic stats
        price_change = ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] != 0 else 0
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        volatility = self._calculate_volatility(prices)

        prompt = f"""
        Analyze this stock price data for {symbol} over the {granularity} period:

        Price data: {prices[:20]}... (showing first 20 of {len(prices)} points)
        Total price change: {price_change:.2f}%
        Average volume: {avg_volume:,.0f}
        Volatility: {volatility:.4f}

        Please provide a concise but insightful summary of this period's price action, including:
        1. Overall trend direction and strength
        2. Key price levels and ranges
        3. Volume patterns and significance
        4. Notable market behavior or patterns
        5. Potential implications for future price movement

        Keep the summary under 150 words and focus on actionable insights.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI summary generation failed: {e}")
            return self._generate_basic_summary(symbol, period_data, granularity)

    def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embeddings using OpenAI."""
        if not self.openai_client:
            return self._generate_basic_embedding(text)

        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"OpenAI embedding generation failed: {e}")
            return self._generate_basic_embedding(text)

    def _generate_basic_summary(self, symbol: str, period_data: List[dict], granularity: str) -> str:
        """Fallback basic summary generation."""
        prices = [item["close"] for item in period_data]
        if not prices:
            return f"No data available for {symbol} {granularity} period."

        price_change = ((prices[-1] - prices[0]) / prices[0]) * 100 if prices[0] != 0 else 0
        direction = "up" if price_change > 0 else "down"
        magnitude = "strongly" if abs(price_change) > 5 else "moderately" if abs(price_change) > 1 else "slightly"

        return f"{symbol} {magnitude} trending {direction} with {price_change:.1f}% price change over {len(prices)} {granularity} periods."

    def _generate_basic_embedding(self, text: str) -> List[float]:
        """Fallback basic embedding generation."""
        # Simple hash-based embedding for fallback
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        # Convert to float list between -1 and 1
        return [(b / 127.5) - 1 for b in hash_bytes[:128]]  # 128 dimensions

    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility."""
        if len(prices) < 2:
            return 0.0

        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                returns.append((prices[i] - prices[i-1]) / prices[i-1])

        if not returns:
            return 0.0

        return math.sqrt(sum(r * r for r in returns) / len(returns))

    def generate(self, symbol: str, granularity: str, period_days: int = 30) -> list[dict]:
        """
        Enhanced summaries with AI-powered analysis and embeddings.
        Uses OpenAI for intelligent summaries when available.
        """
        # Generate data for summarization (last N days)
        end_date = datetime.now().date().isoformat()
        start_date = (datetime.now().date() - timedelta(days=period_days)).isoformat()

        rows = DataService().fetch(symbol, start_date, end_date, "daily")
        if not rows:
            return []

        bucketed: Dict[str, List[dict]] = defaultdict(list)
        for r in rows:
            ts = datetime.fromisoformat(r["ts"])
            if granularity == "weekly":
                key = f"{ts.year}-W{ts.isocalendar().week:02d}"
            elif granularity == "monthly":
                key = f"{ts.year}-{ts.month:02d}"
            else:
                key = ts.date().isoformat()
            bucketed[key].append(r)

        summaries: List[dict] = []
        for key, items in sorted(bucketed.items()):
            opens = [x["open"] for x in items]
            highs = [x["high"] for x in items]
            lows = [x["low"] for x in items]
            closes = [x["close"] for x in items]

            # Calculate returns and volatility
            returns = []
            for i in range(1, len(closes)):
                prev = closes[i - 1]
                cur = closes[i]
                if prev:
                    returns.append((cur - prev) / prev)
            vol = float(math.sqrt(sum(r * r for r in returns) / len(returns))) if returns else 0.0

            # Basic stats
            stats = {
                "open": opens[0],
                "high": max(highs),
                "low": min(lows),
                "close": closes[-1],
                "mean_close": sum(closes) / len(closes),
                "count": len(items),
                "mean_return": sum(returns) / len(returns) if returns else 0.0,
                "volatility": vol,
                "total_volume": sum(x.get("volume", 0) for x in items),
                "price_range": max(highs) - min(lows),
                "trend_strength": abs(sum(returns)) / len(returns) if returns else 0.0
            }

            # Generate AI-powered summary
            ai_summary = self._generate_openai_summary(symbol, items, granularity)

            # Generate AI-powered embedding for the summary
            embedding_vector = self._generate_openai_embedding(ai_summary)

            # Store vector with enhanced metadata
            vector_key = f"{symbol}_{granularity}_{key}"
            metadata = {
                "symbol": symbol,
                "granularity": granularity,
                "period": key,
                "period_start": min(r["ts"] for r in items),
                "period_end": max(r["ts"] for r in items),
                "stats": stats,
                "ai_summary": ai_summary,
                "data_points": len(items),
                "generated_at": datetime.now().isoformat()
            }
            SqliteJsonVectorStore().upsert(vector_key, embedding_vector, metadata)

            summaries.append({
                "symbol": symbol,
                "granularity": granularity,
                "period": key,
                "stats": stats,
                "ai_summary": ai_summary,
                "embedding_dim": len(embedding_vector)
            })

        return summaries


