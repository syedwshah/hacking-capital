from typing import List, Dict
from sqlalchemy.orm import Session
from app.db.models import Vector


class VectorRepository:
    def upsert(self, session: Session, key: str, vector: list[float], metadata: dict) -> None:
        obj = session.get(Vector, key)
        if obj is None:
            obj = Vector(key=key, vector=vector, meta_json=metadata)
            session.add(obj)
        else:
            obj.vector = vector
            obj.meta_json = metadata
        session.commit()

    def list(self, session: Session) -> list[dict]:
        q = session.query(Vector)
        return [{"key": v.key, "vector": v.vector, "metadata": v.meta_json} for v in q.all()]


