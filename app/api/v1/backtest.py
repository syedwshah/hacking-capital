from fastapi import APIRouter
from app.services.backtest_service import BacktestService

router = APIRouter(tags=["backtest"])


@router.post("/backtest/run")
def backtest_run(payload: dict) -> dict:
    symbol = payload.get("symbol")
    start_date = payload.get("start_date", "2020-01-01")
    end_date = payload.get("end_date", "2020-02-01")
    initial_cash = float(payload.get("initial_cash", 1000.0))
    result = BacktestService().run(symbol, start_date, end_date, initial_cash)
    return result
