from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import Decision


class DecisionRepository:
    def insert(self, session: Session, symbol: str, action: str, quantity: float, confidence: float, reason: str, ts: datetime | None = None) -> None:
        obj = Decision(
            symbol=symbol,
            ts=ts or datetime.utcnow(),
            action=action,
            quantity=quantity,
            confidence=confidence,
            reason=reason,
        )
        session.add(obj)
        session.commit()

    def list_for_symbol(self, session: Session, symbol: str) -> list[dict]:
        q = session.query(Decision).filter(Decision.symbol == symbol).order_by(Decision.ts.desc())
        return [
            {"symbol": x.symbol, "ts": x.ts.isoformat(), "action": x.action, "quantity": x.quantity, "confidence": x.confidence, "reason": x.reason}
            for x in q.all()
        ]


