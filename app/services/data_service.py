from __future__ import annotations

import datetime as dt
from typing import List, Dict


class DataService:
    def fetch(self, symbol: str, start_date: str, end_date: str, interval: str) -> list[dict]:
        """
        Deterministic synthetic time-series fallback.
        Generates OHLCV bars with a gentle trend and seasonality.
        """
        start = _parse_dt(start_date)
        end = _parse_dt(end_date)
        if end <= start:
            return []
        step = dt.timedelta(minutes=1) if interval in {"1m", "minute"} else dt.timedelta(days=1)
        t = start
        rows: List[Dict] = []
        price = 100.0
        i = 0
        while t <= end:
            base = 0.02 if interval in {"1m", "minute"} else 0.2
            drift = 0.0001 * i
            seasonal = 0.5 * _sinus(i, period=390 if interval in {"1m", "minute"} else 30)
            delta = base + drift + seasonal * 0.01
            open_p = price
            close_p = max(1.0, open_p + delta)
            high_p = max(open_p, close_p) + 0.05
            low_p = min(open_p, close_p) - 0.05
            volume = 1000 + (i % 100) * 10
            rows.append(
                {
                    "symbol": symbol,
                    "ts": t.isoformat(),
                    "open": round(open_p, 4),
                    "high": round(high_p, 4),
                    "low": round(low_p, 4),
                    "close": round(close_p, 4),
                    "volume": volume,
                    "interval": interval,
                }
            )
            price = close_p
            t += step
            i += 1
        return rows


def _parse_dt(s: str) -> dt.datetime:
    if len(s) == 10:
        return dt.datetime.fromisoformat(s)
    return dt.datetime.fromisoformat(s.replace("Z", ""))


def _sinus(i: int, period: int) -> float:
    import math

    return math.sin(2 * math.pi * (i % period) / period)


