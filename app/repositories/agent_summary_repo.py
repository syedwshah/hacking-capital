from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from app.db.models import AgentSummary


class AgentSummaryRepository:
    def insert_many(self, session: Session, rows: List[Dict]) -> None:
        session.add_all(
            [
                AgentSummary(
                    symbol=r["symbol"],
                    agent=r["agent"],
                    granularity=r["granularity"],
                    ts=r.get("ts") or datetime.utcnow(),
                    reason=r.get("reason", ""),
                    stats_json=r.get("stats", {}),
                )
                for r in rows
            ]
        )
        session.commit()

    def list(self, session: Session, symbol: str, granularity: str) -> list[dict]:
        q = (
            session.query(AgentSummary)
            .filter(AgentSummary.symbol == symbol, AgentSummary.granularity == granularity)
            .order_by(AgentSummary.ts.desc())
        )
        return [
            {
                "symbol": x.symbol,
                "agent": x.agent,
                "granularity": x.granularity,
                "ts": x.ts.isoformat(),
                "reason": x.reason,
                "stats": x.stats_json,
            }
            for x in q.all()
        ]


