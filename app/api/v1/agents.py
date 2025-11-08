from fastapi import APIRouter

router = APIRouter(tags=["agents"])


@router.get("/agents/weights")
def get_weights() -> dict:
    # Placeholder: return empty weights
    return {"weights": []}


@router.post("/agents/weights")
def set_weights(payload: dict) -> dict:
    # Placeholder: accept weights payload
    return {"ok": True, "weights": payload}


@router.get("/agents/summaries")
def agent_summaries(symbol: str, granularity: str) -> dict:
    # Placeholder summaries aggregation
    return {"symbol": symbol, "granularity": granularity, "agents": []}


