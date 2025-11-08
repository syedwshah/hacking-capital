from pydantic import BaseModel


class TradeDecision(BaseModel):
    action: str
    quantity: float
    confidence: float
    reason: str


class TradeEvent(BaseModel):
    ts: str
    action: str
    price: float
    quantity: float
    fees: float = 0.0


class PortfolioSnapshot(BaseModel):
    ts: str
    cash: float
    equity: float
    positions: dict


