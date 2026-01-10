import logging
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from schemas.trade import OperationType, Trade

logger = logging.getLogger(__name__)


class GoogleSheetsService:
    """Service for interacting with Google Sheets"""

    def __init__(self, credentials_path: str, spreadsheet_id: str):
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)

        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(spreadsheet_id)

    def fetch_trades(self, worksheet_name: str = "Trades") -> list[Trade]:
        """Fetches trades from a Google Sheets worksheet"""

        ws = self.sheet.worksheet(worksheet_name)

        rows = ws.get_all_records(value_render_option="FORMATTED_VALUE")

        logger.info("Fetched %d trades", len(rows))
        logger.info("First trade: %s", rows[0] if rows else None)

        trades = []
        for row in rows:
            try:
                date_str = str(row["date"])
                trade_date = datetime.strptime(date_str, "%d.%m.%Y").date()
                operation = OperationType(str(row["operation"]).upper())

                trades.append(
                    Trade(
                        ticker=str(row["ticker"]),
                        date=trade_date,
                        price=float(row["price"]) / 100,
                        quantity=int(row["quantity"]),
                        fee=float(row.get("fee", 0.0)) / 100,
                        operation=operation,
                    )
                )
            except Exception as e:
                print(f"Skipping row due to missing key: {e}")
        return trades

    def write_portfolio_index(
        self, rows: list[tuple[str, float]], worksheet_name: str = "Portfolio Index"
    ):
        try:
            ws = self.sheet.worksheet(worksheet_name)
        except gspread.WorksheetNotFound:
            ws = self.sheet.add_worksheet(title=worksheet_name, rows=1000, cols=2)

        ws.clear()
        ws.append_row(["datetime", "index_value"])
        ws.append_rows(rows)

    def resolve_tickers(self):
        trades = self.fetch_trades()
        return sorted({t.ticker for t in trades})
