import gspread
from google.oauth2.service_account import Credentials

from schemas.trade import Trade


class GoogleSheetsService:
    """Service for interacting with Google Sheets"""

    def __init__(self, credentials_path: str, spreadsheet_id: str):
        scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

        creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)

        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(spreadsheet_id)

    def fetch_trades(self, worksheet_name: str = "Trades") -> list[Trade]:
        """Fetches trades from a Google Sheets worksheet"""

        ws = self.sheet.worksheet(worksheet_name)

        rows = ws.get_all_records()

        trades = []
        for row in rows:
            try:
                trades.append(
                    Trade(
                        ticker=row["ticker"],
                        date=row["date"],
                        price=row["price"],
                        quantity=row["quantity"],
                        fee=row.get("fee", 0.0),
                        operation=row["operation"],
                    )
                )
            except Exception as e:
                print(f"Skipping row due to missing key: {e}")
        return trades
