import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def hourly_candle_update(backfill_service, tickers: list[str]):
    logger.info("Starting hourly candle update")

    backfill_service.backfill_many(tickers)

    logger.info("Hourly candle update finished")


def portfolio_snapshot_job(snapshot_service):
    logger.info("Starting portfolio snapshot job")
    at = datetime.now(timezone.utc)

    saved = snapshot_service.save_snapshot(at)

    if saved:
        logger.info("Portfolio snapshot saved at %s", at)
    else:
        logger.error("Portfolio snapshot already exists at %s", at)
