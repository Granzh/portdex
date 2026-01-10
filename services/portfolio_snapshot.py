from datetime import datetime, timezone

from portfolio.builder import PortfolioBuilder
from services.google_sheets import GoogleSheetsService
from storage.portfolio_snapshot_storage import PortfolioSnapshotStorage


class PortfolioSnapshotService:
    """Service for taking portfolio snapshots"""

    def __init__(
        self,
        sheets: GoogleSheetsService,
        builder: PortfolioBuilder,
        storage: PortfolioSnapshotStorage,
    ):
        self.sheets = sheets
        self.builder = builder
        self.storage = storage

    def take_snapshot(self, at: datetime | None = None) -> bool:
        """Takes a portfolio snapshot"""

        if at is None:
            at = datetime.now(timezone.utc)
        trades = self.sheets.fetch_trades()
        snapshot = self.builder.snapshot(trades, at)
        return self.storage.save(snapshot)
