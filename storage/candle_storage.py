from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import Session

from db.models import Candle
from schemas.candle import CandleDTO


class CandleStorage:
    def __init__(self, session: Session):
        self.session = session

    def upsert_many(self, candles: list[CandleDTO]) -> int:
        if not candles:
            return 0

        stmt = insert(Candle).values(
            [
                {
                    "ticker": c.ticker,
                    "datetime": c.datetime,
                    "interval": c.interval,
                    "open": c.open,
                    "high": c.high,
                    "low": c.low,
                    "close": c.close,
                    "volume": c.volume,
                }
                for c in candles
            ]
        )

        stmt = stmt.on_conflict_do_nothing(
            index_elements=["ticker", "datetime", "interval"]
        )

        result = self.session.execute(stmt)
        self.session.commit()

        return result.rowcount or 0

    def get_last_datetime(self, *, ticker: str, interval: int):
        stmt = (
            select(Candle.datetime)
            .where(Candle.ticker == ticker, Candle.interval == interval)
            .order_by(desc(Candle.datetime))
            .limit(1)
        )

        result = self.session.execute(stmt).scalar_one_or_none()
        return result

    def get_candle(self, *, ticker: str, at: datetime):
        stmt = select(Candle).where(
            Candle.ticker == ticker,
            Candle.datetime == at,
        )

        result = self.session.execute(stmt).scalar_one_or_none()
        return result
