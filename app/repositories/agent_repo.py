from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from app.db.models import AgentWeight as AgentWeightModel


class AgentWeightRepository:
    def get_all(self, session: Session) -> list[dict]:
        q = session.query(AgentWeightModel)
        return [{"agent": x.agent, "weight": x.weight, "version": x.version, "updated_at": x.updated_at.isoformat()} for x in q.all()]

    def upsert_many(self, session: Session, items: List[Dict]) -> None:
        for it in items:
            obj = session.get(AgentWeightModel, it["agent"])
            if obj is None:
                obj = AgentWeightModel(agent=it["agent"], weight=float(it["weight"]), version=it.get("version", "v1"), updated_at=datetime.utcnow())
                session.add(obj)
            else:
                obj.weight = float(it["weight"])
                obj.version = it.get("version", obj.version)
                obj.updated_at = datetime.utcnow()
        session.commit()


