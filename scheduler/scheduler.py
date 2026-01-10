import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from scheduler.jobs import (
    hourly_candle_update,
    portfolio_index_job,
    portfolio_snapshot_job,
)

logger = logging.getLogger(__name__)


def start_scheduler(
    backfill_service, snapshot_service, index_service, tickers: list[str]
) -> None:
    """Starts the scheduler"""

    scheduler = BlockingScheduler()

    # candles
    job = scheduler.add_job(
        func=hourly_candle_update,
        trigger=CronTrigger(minute=5),
        kwargs={"backfill_service": backfill_service, "tickers": tickers},
        id="hourly_candle_update",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    # portfolio snapshot
    job = scheduler.add_job(
        func=portfolio_snapshot_job,
        trigger=CronTrigger(minute=10),
        kwargs={"snapshot_service": snapshot_service},
        id="portfolio_snapshot",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    # portfolio index
    job = scheduler.add_job(
        func=portfolio_index_job,
        trigger=CronTrigger(minute=12),
        kwargs={"index_service": index_service, "snapshot_storage": snapshot_service},
        id="portfolio_index",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    logger.info("Scheduler started")

    scheduler.start()

    scheduler_job = scheduler.get_job(job.id)
    logger.info("Job %s scheduled, next run at %s", job.id, scheduler_job.next_run_time)
