from __future__ import annotations

from typing import List, Dict
from sqlalchemy.orm import Session
from app.db.base import get_session
from app.repositories.vector_repo import VectorRepository


class SqliteJsonVectorStore:
    # Stores vectors as JSON in SQLite via repository (cosine similarity stub)
    def upsert(self, key: str, vector: list[float], metadata: dict) -> None:
        with get_session() as session:  # type: Session
            VectorRepository().upsert(session, key, vector, metadata)

    def query(self, vector: list[float], top_k: int = 10, where: dict | None = None) -> list[dict]:
        # Simple nearest by L2 distance (in-Python for hackathon)
        with get_session() as session:  # type: Session
            items = VectorRepository().list(session)
        def l2(a: list[float], b: list[float]) -> float:
            import math
            n = min(len(a), len(b))
            return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(n)))
        scored = [{"key": it["key"], "metadata": it["metadata"], "distance": l2(vector, it["vector"])} for it in items]
        scored.sort(key=lambda x: x["distance"])
        return scored[:top_k]


