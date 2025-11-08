from typing import List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import Trade


class TradeRepository:
    def insert(self, session: Session, symbol: str, action: str, price: float, quantity: float, fees: float = 0.0, ts: datetime | None = None) -> None:
        obj = Trade(symbol=symbol, ts=ts or datetime.utcnow(), action=action, price=price, quantity=quantity, fees=fees)
        session.add(obj)
        session.commit()

    def list_for_symbol(self, session: Session, symbol: str) -> list[dict]:
        q = session.query(Trade).filter(Trade.symbol == symbol).order_by(Trade.ts.desc())
        return [{"symbol": x.symbol, "ts": x.ts.isoformat(), "action": x.action, "price": x.price, "quantity": x.quantity, "fees": x.fees} for x in q.all()]


