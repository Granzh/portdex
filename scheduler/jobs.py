import logging
from datetime import datetime, timezone

from services.backfill import CandleBackfillService

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


def portfolio_snapshot_job(snapshot_service) -> None:
    """Saves a portfolio snapshot"""
    logger.info("Starting portfolio snapshot job")
    at = datetime.now(timezone.utc)

    saved = snapshot_service.save_snapshot(at)

    if saved:
        logger.info("Portfolio snapshot saved at %s", at)
    else:
        logger.error("Portfolio snapshot already exists at %s", at)


def portfolio_index_job(index_service, snapshot_storage) -> None:
    """Calculates and saves the portfolio index"""
    logger.info("Starting portofolio index job")

    snapshot = snapshot_storage.get_last()

    if not snapshot:
        return

    saved = index_service.calculate_and_save(snapshot)

    if saved:
        logger.info("Index calculated for %s", snapshot.datetime)
