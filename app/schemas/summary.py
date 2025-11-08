from pydantic import BaseModel


class Summary(BaseModel):
    symbol: str
    granularity: str  # daily/weekly/monthly
    period_start: str
    period_end: str
    stats: dict


