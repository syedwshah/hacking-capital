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

    def list_recent(self, session: Session, symbol: str | None = None, limit: int = 50) -> list[Decision]:
        """Get recent decisions, optionally filtered by symbol."""
        q = session.query(Decision).order_by(Decision.ts.desc()).limit(limit)
        if symbol:
            q = q.filter(Decision.symbol == symbol)
        return q.all()

    def list_after_date(self, session: Session, cutoff_date: datetime, symbol: str | None = None) -> list[Decision]:
        """Get decisions after a specific date."""
        q = session.query(Decision).filter(Decision.ts >= cutoff_date).order_by(Decision.ts.desc())
        if symbol:
            q = q.filter(Decision.symbol == symbol)
        return q.all()


