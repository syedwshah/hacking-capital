from fastapi import APIRouter

router = APIRouter(tags=["backtest"])


@router.post("/backtest/run")
def backtest_run(payload: dict) -> dict:
    # Placeholder backtest
    return {"final_cash": payload.get("initial_cash", 1000), "trades": [], "summary": "stub"}


