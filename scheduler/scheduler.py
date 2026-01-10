import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from scheduler.jobs import (
    export_index_to_sheets_job,
    hourly_candle_update,
    portfolio_index_job,
    portfolio_snapshot_job,
)
from storage.portfolio_snapshot_storage import PortfolioSnapshotStorage

logger = logging.getLogger(__name__)


def start_scheduler(
    backfill_service,
    snapshot_service,
    index_service,
    index_export_service,
    snapshot_storage,
) -> None:
    """Starts the scheduler"""

    scheduler = BlockingScheduler()

    tickers = index_service.resolve_tickers() or [
        "SBER",
        "GAZP",
        "LKOH",
        "ROSN",
        "AFKS",
        "MDMG",
        "TRNFP",
        "YDEX",
        "PLZL",
        "DOMRF",
        "TATN",
        "PHOR",
    ]

    # candles
    job = scheduler.add_job(
        func=hourly_candle_update,
        trigger=CronTrigger(minute=20),
        kwargs={"backfill_service": backfill_service, "tickers": tickers},
        id="hourly_candle_update",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    # portfolio snapshot
    job = scheduler.add_job(
        func=portfolio_snapshot_job,
        trigger=CronTrigger(minute=21),
        kwargs={"snapshot_service": snapshot_service},
        id="portfolio_snapshot",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    # portfolio index
    job = scheduler.add_job(
        func=portfolio_index_job,
        trigger=CronTrigger(minute=22),
        kwargs={"index_service": index_service, "snapshot_storage": snapshot_storage},
        id="portfolio_index",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    # portfolio index export
    job = scheduler.add_job(
        func=export_index_to_sheets_job,
        trigger=CronTrigger(minute=23),
        kwargs={"export_service": index_export_service},
        id="portfolio_index_export",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    logger.info("Scheduler started")

    scheduler.start()

    scheduler_job = scheduler.get_job(job.id)
    logger.info("Job %s scheduled, next run at %s", job.id, scheduler_job.next_run_time)
