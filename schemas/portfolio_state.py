from datetime import datetime

from pydantic import BaseModel


class PortfolioState(BaseModel):
    datetime: datetime
    positions: dict[str, float]
    total_value: float
