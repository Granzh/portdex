import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from scheduler.jobs import hourly_candle_update

logger = logging.getLogger(__name__)


def start_scheduler(backfill_service, tickers: list[str]):
    scheduler = BlockingScheduler()

    job = scheduler.add_job(
        func=hourly_candle_update,
        trigger=CronTrigger(minute=5),
        kwargs={"backfill_service": backfill_service, "tickers": tickers},
        id="hourly_candle_update",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    logger.info("Scheduler started")

    scheduler.start()

    scheduler_job = scheduler.get_job(job.id)
    logger.info("Job %s scheduled, next run at %s", job.id, scheduler_job.next_run_time)
