from datetime import datetime, timedelta

from tqdm import tqdm

from services.portfolio_snapshot import PortfolioSnapshotService


class PortfolioSnapshotBackfillService:
    def __init__(self, snapshot_service: PortfolioSnapshotService):
        self.snapshot_service = snapshot_service

    def backfill(self, start: datetime, end: datetime, step: timedelta):
        trades = self.snapshot_service.sheets.fetch_trades()

        total_steps = int((end - start) / step) + 1
        t = start
        for _ in tqdm(
            range(total_steps), desc="Backfilling snapshots", unit="snapshot"
        ):
            self.snapshot_service.take_snapshot(t, trades)
            t += step
