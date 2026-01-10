import logging
from datetime import datetime

from db.models import PortfolioIndex, PortfolioSnapshot
from storage.candle_storage import CandleStorage
from storage.portfolio_index_storage import PortfolioIndexStorage
from storage.portfolio_snapshot_storage import PortfolioSnapshotStorage

logger = logging.getLogger(__name__)


class IndexService:
    """Service for calculating and saving the portfolio index"""

    def __init__(
        self,
        snapshot_storage: PortfolioSnapshotStorage,
        index_storage: PortfolioIndexStorage,
        candle_storage: CandleStorage,
        base: float = 1000.0,
    ):
        self.snapshot_storage = snapshot_storage
        self.index_storage = index_storage
        self.candle_storage = candle_storage
        self.base = base

    def _get_base_snapshot(self):
        """Fetches the first portfolio snapshot"""

        return self.snapshot_storage.get_first()

    def _valuate_positions(self, positions, at: datetime) -> float:
        total = 0.0

        for pos in positions:
            candle = self.candle_storage.get_last_before(ticker=pos.ticker, at=at)
            if candle is None:
                logger.error("No candle found for ticker %s at %s", pos.ticker, at)
                continue
            total += pos.quantity * candle.close

        return total

    def calculate_and_save(self, snapshot):
        """Calculates and saves the portfolio index"""
        logger.info("Calculating index for snapshot at %s", snapshot.datetime)

        base_snapshot = self._get_base_snapshot()

        if base_snapshot is None:
            logger.info("Initializing base index")
            index_value = self.base
        else:
            index_value = self.calculate(snapshot, base_snapshot)
        index = PortfolioIndex(datetime=snapshot.datetime, index_value=index_value)

        return self.index_storage.save(index)

    def calculate(self, snapshot: PortfolioSnapshot, base_snapshot: PortfolioSnapshot):
        base_value_now = self._valuate_positions(
            base_snapshot.positions, snapshot.datetime
        )
        if base_snapshot.total_value == 0:
            raise ValueError("Base snapshot total value cannot be zero")
        return (base_value_now / base_snapshot.total_value) * self.base

    def save(self, snapshot, index_value):
        index = PortfolioIndex(datetime=snapshot.datetime, index_value=index_value)

        return self.index_storage.save(index)
