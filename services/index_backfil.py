from sys import stdout

from tqdm import tqdm

from db.models import PortfolioIndex
from services.index import IndexService


class IndexBackfillService:
    def __init__(self, snapshot_storage, index_service: IndexService):
        self.snapshot_storage = snapshot_storage
        self.index_service = index_service

    def backfill(self):
        snapshots = self.snapshot_storage.get_all_ordered()

        base_snapshot = next(
            s for s in snapshots if s.total_value > 0 and s.cash_flow == 0
        )

        base_index_value = self.index_service.base
        divisor = base_snapshot.total_value / base_index_value

        self.index_service.save_from_snapshot(
            snapshot=base_snapshot,
            index_value=base_index_value,
            divisor=divisor,
        )

        prev_index = PortfolioIndex(
            datetime=base_snapshot.datetime,
            index_value=base_index_value,
            divisor=divisor,
        )

        for snapshot in tqdm(
            (s for s in snapshots if s.datetime > base_snapshot.datetime),
            desc="Backfilling index",
            unit="snapshot",
        ):
            index_value, divisor = self.index_service.calculate(snapshot, prev_index)

            self.index_service.save_from_snapshot(
                snapshot=snapshot,
                index_value=index_value,
                divisor=divisor,
            )

            prev_index = PortfolioIndex(
                datetime=snapshot.datetime,
                index_value=index_value,
                divisor=divisor,
            )
