from datetime import datetime, timezone

from portfolio.builder import PortfolioBuilder
from schemas.trade import Trade
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

    from datetime import datetime, timezone

    def take_snapshot(
        self,
        at: datetime | None = None,
        trades: list[Trade] | None = None,
    ) -> bool:
        """Takes a portfolio snapshot with period cash flow"""

        if at is None:
            at = datetime.now(timezone.utc)

        if trades is None:
            trades = self.sheets.fetch_trades()

        prev_snapshot = self.storage.get_last_before(at)
        prev_at = prev_snapshot.datetime if prev_snapshot else None

        snapshot = self.builder.snapshot(
            trades=trades,
            at=at,
            prev_at=prev_at,
        )

        return self.storage.save(snapshot)
