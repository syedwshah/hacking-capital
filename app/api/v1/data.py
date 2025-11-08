from fastapi import APIRouter
from app.services.data_service import DataService

router = APIRouter(tags=["data"])


@router.post("/data/fetch")
def fetch_data(payload: dict) -> dict:
    symbol = payload.get("symbol")
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    interval = payload.get("interval", "daily")
    rows = DataService().fetch(symbol, start_date, end_date, interval)
    return {"symbol": symbol, "rows": rows}


