import logging

from db.models import PortfolioIndex
from storage.portfolio_index_storage import PortfolioIndexStorage
from storage.portfolio_snapshot_storage import PortfolioSnapshotStorage

logger = logging.getLogger(__name__)


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
        logger.info("Calculating index for snapshot at %s", snapshot.datetime)

        base_snapshot = self._get_base_snapshot()

        if base_snapshot is None:
            logger.info("Initializing base index")
            index_value = self.base
        else:
            index_value = (snapshot.total_value / base_snapshot.total_value) * self.base

        index = PortfolioIndex(datetime=snapshot.datetime, index_value=index_value)

        return self.index_storage.save(index)

    def calculate(self, snapshot, base_snapshot):
        if base_snapshot.total_value == 0:
            raise ValueError("Base snapshot total value cannot be zero")
        return (snapshot.total_value / base_snapshot.total_value) * self.base

    def save(self, snapshot, index_value):
        index = PortfolioIndex(datetime=snapshot.datetime, index_value=index_value)

        return self.index_storage.save(index)
