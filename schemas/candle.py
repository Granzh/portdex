from datetime import datetime

from pydantic import BaseModel


class CandleDTO(BaseModel):
    ticker: str
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
