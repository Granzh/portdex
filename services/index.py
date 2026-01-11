import logging
from datetime import datetime
from decimal import DivisionByZero

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

    def calculate(
        self,
        snapshot: PortfolioSnapshot,
        prev_index: PortfolioIndex,
    ):
        market_cap = snapshot.total_value

        if market_cap == 0:
            return prev_index.index_value, prev_index.divisor

        prev_index_value = prev_index.index_value
        prev_divisor = prev_index.divisor
        if snapshot.cash_flow != 0:
            divisor = (market_cap - snapshot.cash_flow) / prev_index_value
        else:
            divisor = prev_divisor
        index_value = market_cap / divisor

        return index_value, divisor

    def save_from_snapshot(self, snapshot, index_value: float, divisor: float):
        index = PortfolioIndex(
            datetime=snapshot.datetime,
            index_value=index_value,
            divisor=divisor,
        )

        return self.index_storage.save(index)
