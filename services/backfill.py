import logging
from datetime import datetime, timedelta, timezone

from db.models import Candle
from services.moex import MoexService
from storage.candle_storage import CandleStorage
from storage.security_storage import SecurityStorage

logger = logging.getLogger(__name__)


class CandleBackfillService:
    """Service for backfilling candle data"""

    def __init__(
        self,
        *,
        moex: MoexService,
        candle_storage: CandleStorage,
        security_storage: SecurityStorage,
        interval: int = 60,
        default_start: datetime,
    ):
        self.moex = moex
        self.candle_storage = candle_storage
        self.security_storage = security_storage
        self.interval = interval
        self.default_start = default_start

    def backfill_ticker(self, ticker: str):
        """Method for backfilling candle data for a given ticker"""
        self.security_storage.get_or_create(ticker=ticker)

        last_dt = self.candle_storage.get_last_datetime(
            ticker=ticker, interval=self.interval
        )

        start_dt = last_dt or self.default_start
        end_dt = datetime.now(tz=timezone.utc)

        logger.info(
            "Backfillling %s from %s to %s",
            ticker,
            start_dt,
            end_dt,
        )

        dtos = self.moex.fetch_candles(
            ticker=ticker,
            start=start_dt,
            end=end_dt,
            interval=self.interval,
        )

        candles = [
            Candle(
                ticker=ticker,
                datetime=dt.datetime,
                open=dt.open,
                high=dt.high,
                low=dt.low,
                close=dt.close,
                volume=dt.volume,
                interval=self.interval,
            )
            for dt in dtos
        ]

        inserted = self.candle_storage.upsert_many(candles)

        logger.info(
            "Inserted %d candles for %s",
            inserted,
            ticker,
        )

    def backfill_many(self, tickers: list[str]):
        """Method for backfilling candle data for multiple tickers"""

        for ticker in tickers:
            try:
                self.backfill_ticker(ticker)
            except Exception as e:
                logger.error("Failed to backfill %s: %s", ticker, e)
