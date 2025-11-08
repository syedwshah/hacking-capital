import os
import httpx

API_BASE = os.environ.get("API_BASE", "http://localhost:8000/api/v1")


def get_health() -> dict:
    with httpx.Client(timeout=5.0) as client:
        r = client.get(f"{API_BASE}/health")
        r.raise_for_status()
        return r.json()


