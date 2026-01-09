import logging

logger = logging.getLogger(__name__)


def hourly_candle_update(backfill_service, tickers: list[str]):
    logger.info("Starting hourly candle update")

    backfill_service.backfill_many(tickers)

    logger.info("Hourly candle update finished")
