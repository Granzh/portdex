import logging

from services.google_sheets import GoogleSheetsService
from storage.portfolio_index_storage import PortfolioIndexStorage

logger = logging.getLogger(__name__)


class IndexExportService:
    def __init__(
        self, sheets: GoogleSheetsService, index_storage: PortfolioIndexStorage
    ):
        self.sheets = sheets
        self.index_storage = index_storage

    def export_all(self):
        index_rows = self.index_storage.get_all_ordered()
        logger.info("Exporting %d index rows", len(index_rows))
        rows = [(row.datetime.isoformat(), row.index_value) for row in index_rows]

        self.sheets.write_portfolio_index(rows)
