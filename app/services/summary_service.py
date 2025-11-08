from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import List, Dict

from app.services.data_service import DataService


class SummaryService:
    def generate(self, symbol: str, granularity: str) -> list[dict]:
        """
        Minimal deterministic summaries using synthetic data as input.
        Produces OHLC and simple stats aggregated by day/week/month.
        """
        # Generate a short window of data to summarize
        rows = DataService().fetch(symbol, "2020-01-01", "2020-02-01", "daily")
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
            stats = {
                "open": opens[0],
                "high": max(highs),
                "low": min(lows),
                "close": closes[-1],
                "mean_close": sum(closes) / len(closes),
                "count": len(items),
            }
            summaries.append({"symbol": symbol, "granularity": granularity, "period": key, "stats": stats})
        return summaries


