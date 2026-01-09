from datetime import datetime

from pydantic import BaseModel


class IndexPoint(BaseModel):
    datetime: datetime
    value: float
