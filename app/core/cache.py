from __future__ import annotations

import time
from typing import Any

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore

from app.core.settings import settings


class KnowledgeCache:
    def __init__(self) -> None:
        self._client = None
        if redis is not None:
            try:
                self._client = redis.from_url(settings.redis_url, decode_responses=True)
            except Exception:
                self._client = None
        self._fallback: dict[str, tuple[float, dict]] = {}

    def _make_key(self, symbol: str, granularity: str) -> str:
        return f"kc:v1:sym:{symbol}:g:{granularity}"

    def get_summary(self, symbol: str, granularity: str) -> dict | None:
        key = self._make_key(symbol, granularity)
        if self._client:
            try:
                data = self._client.get(key)
                if data:
                    import json

                    return json.loads(data)
            except Exception:
                pass
        # fallback
        item = self._fallback.get(key)
        if not item:
            return None
        expires_at, payload = item
        if time.time() > expires_at:
            self._fallback.pop(key, None)
            return None
        return payload

    def set_summary(self, symbol: str, granularity: str, payload: dict, ttl_s: int) -> None:
        key = self._make_key(symbol, granularity)
        if self._client:
            try:
                import json

                self._client.setex(key, ttl_s, json.dumps(payload))
                return
            except Exception:
                pass
        # fallback
        self._fallback[key] = (time.time() + ttl_s, payload)


