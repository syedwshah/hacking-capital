from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from app.db.models import Summary as SummaryModel


class SummaryRepository:
    def insert_many(self, session: Session, rows: List[Dict]) -> None:
        objs = []
        for r in rows:
            period = r.get("period", "")
            # naive parsing: treat period as YYYY-MM-DD if present, else now
            try:
                period_start = datetime.fromisoformat(period + "T00:00:00") if period else datetime.utcnow()
            except Exception:
                period_start = datetime.utcnow()
            period_end = period_start
            objs.append(
                SummaryModel(
                    symbol=r["symbol"],
                    granularity=r["granularity"],
                    period_start=period_start,
                    period_end=period_end,
                    stats_json=r.get("stats", {}),
                )
            )
        session.add_all(objs)
        session.commit()

    def get(self, session: Session, symbol: str, granularity: str) -> list[dict]:
        q = (
            session.query(SummaryModel)
            .filter(SummaryModel.symbol == symbol, SummaryModel.granularity == granularity)
            .order_by(SummaryModel.period_start.desc())
        )
        return [
            {
                "symbol": x.symbol,
                "granularity": x.granularity,
                "period_start": x.period_start.isoformat(),
                "period_end": x.period_end.isoformat(),
                "stats": x.stats_json,
            }
            for x in q.all()
        ]


