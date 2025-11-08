from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.repositories.agent_repo import AgentWeightRepository
from app.repositories.agent_summary_repo import AgentSummaryRepository
from app.core.cache import KnowledgeCache

router = APIRouter(tags=["agents"])


@router.get("/agents/weights")
def get_weights(session: Session = Depends(db_session)) -> dict:
    weights = AgentWeightRepository().get_all(session)
    return {"weights": weights}


@router.post("/agents/weights")
def set_weights(payload: dict, session: Session = Depends(db_session)) -> dict:
    items = payload.get("weights", [])
    AgentWeightRepository().upsert_many(session, items)
    return {"ok": True, "weights": items}


@router.get("/agents/summaries")
def agent_summaries(
    symbol: str = Query(...),
    granularity: str = Query("daily"),
    session: Session = Depends(db_session),
) -> dict:
    cache = KnowledgeCache().get_summary(symbol, granularity) or {}
    records = AgentSummaryRepository().list(session, symbol, granularity)
    return {"symbol": symbol, "granularity": granularity, "cache": cache, "records": records}


