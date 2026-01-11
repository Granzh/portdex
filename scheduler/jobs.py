import logging
from datetime import datetime, timezone

from db.models import PortfolioIndex
from services.backfill import CandleBackfillService
from services.index import IndexService
from services.index_export import IndexExportService
from services.portfolio_snapshot import PortfolioSnapshotService
from storage.portfolio_index_storage import PortfolioIndexStorage
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
    index_service: IndexService,
    snapshot_storage: PortfolioSnapshotStorage,
    index_storage: PortfolioIndexStorage,
) -> None:
    """Calculates and saves the portfolio index"""
    logger.info("Starting portofolio index job")

    snapshot = snapshot_storage.get_last()
    if snapshot is None:
        logger.warning("Snapshot not found")
        return

    prev_index = index_storage.get_last()
    if prev_index is None:
        logger.info("Initializing portfolio index")
        index = PortfolioIndex(
            datetime=snapshot.datetime,
            index_value=index_service.base,
            divisor=snapshot.total_value / index_service.base,
        )

        index_storage.save(index)
        return

    index_value, divisor = index_service.calculate(snapshot, prev_index)
    index = PortfolioIndex(
        datetime=snapshot.datetime, index_value=index_value, divisor=divisor
    )

    index_storage.save(index)

    logger.info("Index calculated at %s: %.2f", index.datetime, index.index_value)


def export_index_to_sheets_job(export_service: IndexExportService) -> None:
    logger.info("Exporting portfolio index to Google Sheets")

    export_service.export_all()

    logger.info("Portfolio index export finished")
