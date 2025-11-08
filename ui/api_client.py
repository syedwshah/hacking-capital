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


