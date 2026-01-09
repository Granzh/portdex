from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Trade(BaseModel):
    ticker: str
    datetime: datetime
    price: float
    quantity: int
    fee: float
    side: Literal["BUY", "SELL"]
