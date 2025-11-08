from fastapi import APIRouter
from app.services.summary_service import SummaryService
from app.core.cache import KnowledgeCache

router = APIRouter(tags=["summaries"])


@router.post("/summaries/generate")
def generate_summaries(payload: dict) -> dict:
    symbol = payload.get("symbol")
    granularity = payload.get("granularity", "daily")
    svc = SummaryService()
    summaries = svc.generate(symbol, granularity)
    # store latest in cache for quick access
    if summaries:
        KnowledgeCache().set_summary(symbol, granularity, {"summaries": summaries}, ttl_s=86400)
    return {"summaries": summaries}


