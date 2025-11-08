import os
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


