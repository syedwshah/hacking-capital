from fastapi import APIRouter

router = APIRouter(tags=["data"])


@router.post("/data/fetch")
def fetch_data(payload: dict) -> dict:
    # Placeholder: accept symbol, start_date, end_date, interval; return stub rows
    return {"symbol": payload.get("symbol"), "rows": []}


