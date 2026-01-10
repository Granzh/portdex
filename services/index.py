from db.models import PortfolioIndex
from storage.portfolio_index_storage import PortfolioIndexStorage
from storage.portfolio_snapshot_storage import PortfolioSnapshotStorage


class IndexService:
    """Service for calculating and saving the portfolio index"""

    def __init__(
        self,
        snapshot_storage: PortfolioSnapshotStorage,
        index_storage: PortfolioIndexStorage,
        base: float = 1000.0,
    ):
        self.snapshot_storage = snapshot_storage
        self.index_storage = index_storage
        self.base = base

    def _get_base_snapshot(self):
        """Fetches the first portfolio snapshot"""

        return self.snapshot_storage.get_first()

    def calculate_and_save(self, snapshot):
        """Calculates and saves the portfolio index"""

        base_snapshot = self._get_base_snapshot()

        if base_snapshot is None:
            return False
        if base_snapshot.total_value == 0:
            return False

        index_value = (snapshot.total_value / base_snapshot.total_value) * self.base

        index = PortfolioIndex(datetime=snapshot.datetime, index_value=index_value)

        return self.index_storage.save(index)

    def backfill(self):
        """Backfills the portfolio index"""

        snapshots = self.snapshot_storage.get_all_ordered()

        base_snapshot = snapshots[0]

        for snapshot in snapshots:
            index_value = (snapshot.total_value / base_snapshot.total_value) * self.base

            index = PortfolioIndex(datetime=snapshot.datetime, index_value=index_value)

            self.index_storage.save(index)
