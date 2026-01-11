import os
from datetime import datetime, timedelta

import typer
from dotenv import load_dotenv
from rich import print

import storage.session as db_session
from portfolio.builder import PortfolioBuilder
from services.google_sheets import GoogleSheetsService
from services.index import IndexService
from services.index_backfil import IndexBackfillService
from services.portfolio_snapshot import PortfolioSnapshotService
from services.portfolio_snapshot_backfill import PortfolioSnapshotBackfillService
from storage.candle_storage import CandleStorage
from storage.portfolio_index_storage import PortfolioIndexStorage
from storage.portfolio_snapshot_storage import PortfolioSnapshotStorage

backfill_app = typer.Typer(help="Backfill historical data")
load_dotenv()
CREDENTIALS_PATH = "credentials.json"
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID")


@backfill_app.command("index")
def backfill_index(
    from_scratch: bool = typer.Option(
        False, "--from-scratch", help="Delete index before backfilling"
    ),
):
    print("[bold blue]Starting index backfill[/bold blue]")

    db_session.init_db()

    session = db_session.SessionLocal()

    snapshot_storage = PortfolioSnapshotStorage(session)
    index_storage = PortfolioIndexStorage(session)
    candle_storage = CandleStorage(session)
    index_service = IndexService(snapshot_storage, index_storage, candle_storage)
    backfill_service = IndexBackfillService(
        snapshot_storage=snapshot_storage,
        index_service=index_service,
    )

    if from_scratch:
        print("[yellow]Clearing portfolio_index table[/yellow]")

        index_storage.delete_all()

    backfill_service.backfill()

    print("[green]Index backfill completed[/green]")


@backfill_app.command("snapshot")
def backfill_snapshots(
    start: datetime = typer.Option(..., help="Start datetime (YYYY-MM-DD)"),
    end: datetime = typer.Option(..., help="End datetime (YYYY-MM-DD)"),
    step_minutes: int = typer.Option(60, help="Step in minutes"),
):
    print("[bold blue]Starting snapshot backfill[/bold blue]")

    db_session.init_db()

    session = db_session.SessionLocal()

    candle_storage = CandleStorage(session)
    portfolio_builder = PortfolioBuilder(candle_storage)
    google_sheets_service = GoogleSheetsService(CREDENTIALS_PATH, GOOGLE_SPREADSHEET_ID)
    portfolio_snapshot_storage = PortfolioSnapshotStorage(session)
    snapshot_service = PortfolioSnapshotService(
        google_sheets_service, portfolio_builder, portfolio_snapshot_storage
    )
    backfill_service = PortfolioSnapshotBackfillService(snapshot_service)

    step = timedelta(minutes=step_minutes)

    backfill_service.backfill(start=start, end=end, step=step)

    print("[green]Snapshot backfill completed[/green]")
