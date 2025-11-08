from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import db_session
from app.services.summary_service import SummaryService
from app.core.cache import KnowledgeCache
from app.repositories.summary_repo import SummaryRepository

router = APIRouter(tags=["summaries"])


@router.post("/summaries/generate")
def generate_summaries(payload: dict, session: Session = Depends(db_session)) -> dict:
    symbol = payload.get("symbol")
    granularity = payload.get("granularity", "daily")
    svc = SummaryService()
    summaries = svc.generate(symbol, granularity)
    # store latest in cache for quick access
    if summaries:
        KnowledgeCache().set_summary(symbol, granularity, {"summaries": summaries}, ttl_s=86400)
        SummaryRepository().insert_many(session, summaries)
    return {"summaries": summaries}


