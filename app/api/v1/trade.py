from fastapi import APIRouter

router = APIRouter(tags=["trade"])


@router.post("/trade/decide")
def trade_decide(payload: dict) -> dict:
    # Placeholder decision
    return {"action": "HOLD", "quantity": 0, "confidence": 50, "reason": "stub"}


