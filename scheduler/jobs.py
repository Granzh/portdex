import logging
from datetime import datetime, timezone

from services.backfill import CandleBackfillService
from services.index import IndexService
from services.index_export import IndexExportService
from services.portfolio_snapshot import PortfolioSnapshotService
from storage.portfolio_snapshot_storage import PortfolioSnapshotStorage

logger = logging.getLogger(__name__)


def hourly_candle_update(
    backfill_service: CandleBackfillService, tickers: list[str]
) -> None:
    """
    Updates hourly candle data for the given tickers.
    """

    logger.info("Starting hourly candle update")

    backfill_service.backfill_many(tickers)

    logger.info("Hourly candle update finished")


def portfolio_snapshot_job(snapshot_service: PortfolioSnapshotService) -> None:
    """Saves a portfolio snapshot"""
    logger.info("Starting portfolio snapshot job")
    at = datetime.now(timezone.utc)

    saved = snapshot_service.take_snapshot(at)

    if saved:
        logger.info("Portfolio snapshot saved at %s", at)
    else:
        logger.error("Portfolio snapshot already exists at %s", at)


def portfolio_index_job(
    index_service: IndexService, snapshot_storage: PortfolioSnapshotStorage
) -> None:
    """Calculates and saves the portfolio index"""
    logger.info("Starting portofolio index job")

    snapshot = snapshot_storage.get_last()
    base_snapshot = snapshot_storage.get_first()

    index_value = index_service.calculate(snapshot, base_snapshot)
    index_service.save(snapshot, index_value)


def export_index_to_sheets_job(export_service: IndexExportService) -> None:
    logger.info("Exporting portfolio index to Google Sheets")

    export_service.export_all()

    logger.info("Portfolio index export finished")
