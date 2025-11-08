import os
import json
import httpx

API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


def get_health() -> dict:
    with httpx.Client(timeout=5.0) as client:
        r = client.get(f"{API_BASE}/health")
        r.raise_for_status()
        return r.json()


def decide(symbol: str, granularity: str, cash: float) -> dict:
    with httpx.Client(timeout=10.0) as client:
        r = client.post(f"{API_BASE}/trade/decide", json={"symbol": symbol, "granularity": granularity, "cash": cash})
        r.raise_for_status()
        return r.json()


def get_agent_weights() -> dict:
    with httpx.Client(timeout=5.0) as client:
        r = client.get(f"{API_BASE}/agents/weights")
        r.raise_for_status()
        return r.json()


def set_agent_weights(weights: list[dict]) -> dict:
    with httpx.Client(timeout=5.0) as client:
        r = client.post(f"{API_BASE}/agents/weights", json={"weights": weights})
        r.raise_for_status()
        return r.json()


def simulate_batch(symbols: list[str], steps: int, cash: float) -> dict:
    with httpx.Client(timeout=60.0) as client:
        r = client.post(f"{API_BASE}/simulate/batch", json={"symbols": symbols, "steps": steps, "cash": cash})
        r.raise_for_status()
        return r.json()


def run_backtest(symbol: str, start_date: str, end_date: str, initial_cash: float) -> dict:
    with httpx.Client(timeout=60.0) as client:
        r = client.post(f"{API_BASE}/backtest/run", json={"symbol": symbol, "start_date": start_date, "end_date": end_date, "initial_cash": initial_cash})
        r.raise_for_status()
        return r.json()


def fetch_data(symbol: str, start_date: str, end_date: str, interval: str = "daily") -> dict:
    with httpx.Client(timeout=30.0) as client:
        r = client.post(f"{API_BASE}/data/fetch", json={"symbol": symbol, "start_date": start_date, "end_date": end_date, "interval": interval})
        r.raise_for_status()
        return r.json()


def stream_events(symbol: str, steps: int, cash: float):
    with httpx.Client(timeout=None) as client:
        with client.stream("GET", f"{API_BASE}/simulate/events", params={"symbol": symbol, "steps": steps, "cash": cash}) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data:"):
                    payload = line.split("data:", 1)[1].strip()
                    if payload:
                        yield json.loads(payload)


def get_portfolio_state() -> dict:
    with httpx.Client(timeout=5.0) as client:
        r = client.get(f"{API_BASE}/portfolio/state")
        r.raise_for_status()
        return r.json()


def optimize_mean_variance(symbols: list[str], returns: list[float], covariance: list[list[float]], risk_free_rate: float = 0.02) -> dict:
    with httpx.Client(timeout=10.0) as client:
        r = client.post(f"{API_BASE}/portfolio/optimize/mean-variance", json={
            "symbols": symbols,
            "returns": returns,
            "covariance": covariance,
            "risk_free_rate": risk_free_rate
        })
        r.raise_for_status()
        return r.json()


def optimize_risk_parity(symbols: list[str], covariance: list[list[float]]) -> dict:
    with httpx.Client(timeout=10.0) as client:
        r = client.post(f"{API_BASE}/portfolio/optimize/risk-parity", json={
            "symbols": symbols,
            "covariance": covariance
        })
        r.raise_for_status()
        return r.json()


def get_trading_history(limit: int = 50, symbol: str = None) -> dict:
    params = {"limit": limit}
    if symbol:
        params["symbol"] = symbol
    with httpx.Client(timeout=5.0) as client:
        r = client.get(f"{API_BASE}/trade/history", params=params)
        r.raise_for_status()
        return r.json()


def get_trading_performance(start_date: str = None, end_date: str = None) -> dict:
    params = {}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    with httpx.Client(timeout=5.0) as client:
        r = client.get(f"{API_BASE}/trade/performance", params=params)
        r.raise_for_status()
        return r.json()


def get_simulation_history(limit: int = 10) -> dict:
    with httpx.Client(timeout=5.0) as client:
        r = client.get(f"{API_BASE}/simulate/history", params={"limit": limit})
        r.raise_for_status()
        return r.json()


def generate_summaries(symbol: str, granularity: str = "daily", period_days: int = 30) -> dict:
    with httpx.Client(timeout=30.0) as client:
        r = client.post(f"{API_BASE}/summaries/generate", json={
            "symbol": symbol,
            "granularity": granularity,
            "period_days": period_days
        })
        r.raise_for_status()
        return r.json()


