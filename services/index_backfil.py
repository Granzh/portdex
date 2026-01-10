from sys import stdout

from tqdm import tqdm


class IndexBackfillService:
    def __init__(self, snapshot_storage, index_service):
        self.snapshot_storage = snapshot_storage
        self.index_service = index_service

    def backfill(self):
        snapshots = self.snapshot_storage.get_all_ordered()

        base_snapshot = next((s for s in snapshots if s.total_value > 0), None)
        if base_snapshot is None:
            raise RuntimeError("No valid base snapshot found")

        self.index_service.save(base_snapshot, self.index_service.base)

        snapshots_to_process = [
            s for s in snapshots if s.datetime > base_snapshot.datetime
        ]

        for snapshot in tqdm(
            snapshots_to_process,
            desc="Backfilling index",
            unit="snapshot",
            disable=not stdout.isatty(),
        ):
            index_value = self.index_service.calculate(snapshot, base_snapshot)
            self.index_service.save(snapshot, index_value)
