from fastapi import APIRouter

router = APIRouter(tags=["summaries"])


@router.post("/summaries/generate")
def generate_summaries(payload: dict) -> dict:
    # Placeholder: accept symbol + granularity; return stub summaries
    return {"summaries": []}


