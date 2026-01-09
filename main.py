import logging
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

from portfolio.builder import PortfolioBuilder
from scheduler.scheduler import start_scheduler
from services.backfill import CandleBackfillService
from services.google_sheets import GoogleSheetsService
from services.index import IndexService
from services.moex import MoexService
from services.portfolio_snapshot import PortfolioSnapshotService
from storage.candle_storage import CandleStorage
from storage.index_storage import IndexStorage
from storage.portfolio_index_storage import PortfolioIndexStorage
from storage.portfolio_snapshot_storage import PortfolioSnapshotStorage
from storage.security_storage import SecurityStorage
from storage.session import SessionLocal, init_db

logging.basicConfig(level=logging.INFO)

TICKERS = ["SBER", "GAZP", "LKOH"]

load_dotenv()

CREDENTIALS_PATH = "credentials.json"
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")


def main():
    init_db()

    session = SessionLocal()

    candle_storage = CandleStorage(session)
    backfill_service = CandleBackfillService(
        moex=MoexService(),
        candle_storage=CandleStorage(session),
        security_storage=SecurityStorage(session),
        interval=60,
        default_start=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )

    sheets = GoogleSheetsService(
        credentials_path=CREDENTIALS_PATH,
        spreadsheet_id=GOOGLE_SPREADSHEET_ID,
    )

    builder = PortfolioBuilder(candle_storage)
    snapshot_storage = PortfolioSnapshotStorage(session)
    snapshot_service = PortfolioSnapshotService(
        sheets=sheets, builder=builder, storage=snapshot_storage
    )

    index_storage = PortfolioIndexStorage(session)

    index_service = IndexService(
        snapshot_storage=snapshot_storage,
        index_storage=index_storage,
    )

    start_scheduler(
        backfill_service=backfill_service,
        snapshot_service=snapshot_service,
        index_service=index_service,
        tickers=TICKERS,
    )


if __name__ == "__main__":
    main()
