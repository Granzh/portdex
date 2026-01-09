from datetime import date
from enum import Enum

from pydantic import BaseModel


class OperationType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class Trade(BaseModel):
    ticker: str
    date: date
    price: float
    quantity: int
    fee: float = 0.0
    operation: OperationType
