import logging
from datetime import datetime, timezone

from scheduler.scheduler import start_scheduler
from services.backfill import CandleBackfillService
from services.moex import MoexService
from storage.candle_storage import CandleStorage
from storage.security_storage import SecurityStorage
from storage.session import SessionLocal, init_db

logging.basicConfig(level=logging.INFO)

TICKERS = ["SBER", "GAZP", "LKOH"]


def main():
    init_db()

    session = SessionLocal()

    backfill_service = CandleBackfillService(
        moex=MoexService(),
        candle_storage=CandleStorage(session),
        security_storage=SecurityStorage(session),
        interval=60,
        default_start=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )

    start_scheduler(backfill_service, TICKERS)


if __name__ == "__main__":
    main()
