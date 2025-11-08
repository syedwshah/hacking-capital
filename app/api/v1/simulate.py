from fastapi import APIRouter

router = APIRouter(tags=["simulate"])


@router.post("/simulate/stream")
def simulate_stream(payload: dict) -> dict:
    # Placeholder: would stream events; for now return stub
    return {"events": []}


