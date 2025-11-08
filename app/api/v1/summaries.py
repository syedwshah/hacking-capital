import os
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
    period_days = payload.get("period_days", 30)

    svc = SummaryService()
    summaries = svc.generate(symbol, granularity, period_days)

    # store latest in cache for quick access
    if summaries:
        KnowledgeCache().set_summary(symbol, granularity, {"summaries": summaries}, ttl_s=86400)
        # Update repository to handle new AI summary format
        summary_records = []
        for summary in summaries:
            summary_record = {
                "symbol": summary["symbol"],
                "granularity": summary["granularity"],
                "period_start": summary["period"],
                "period_end": summary["period"],
                "stats_json": {
                    **summary["stats"],
                    "ai_summary": summary.get("ai_summary", ""),
                    "embedding_dim": summary.get("embedding_dim", 0)
                }
            }
            summary_records.append(summary_record)
        SummaryRepository().insert_many(session, summary_records)

    return {"summaries": summaries, "ai_powered": bool(os.getenv("OPENAI_API_KEY"))}


