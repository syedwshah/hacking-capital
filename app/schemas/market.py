from pydantic import BaseModel


class PriceBar(BaseModel):
    symbol: str
    ts: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    interval: str


