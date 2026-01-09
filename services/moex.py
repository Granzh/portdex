from datetime import datetime
from typing import List

import httpx

from schemas.candle import CandleDTO


class MoexService:
    BASE_URL = "https://iss.moex.com/iss"

    def __init__(self, timeout: float = 10.0):
        self.client = httpx.Client(timeout=timeout)

    def fetch_candles(
        self, ticker: str, *, interval: int, start: datetime, end: datetime
    ) -> List[CandleDTO]:
        candles: list[CandleDTO] = []
        offset = 0

        while True:
            data = self._fetch_page(
                ticker=ticker, interval=interval, start=start, end=end, offset=offset
            )

            if not data:
                break

            candles.extend(data)
            offset += len(data)

        return candles

    def _fetch_page(
        self,
        *,
        ticker: str,
        interval: int,
        start: datetime,
        end: datetime,
        offset: int,
    ) -> list[CandleDTO]:
        url = (
            f"{self.BASE_URL}/engines/stock/markets/shares/"
            f"boards/TQBR/securities/{ticker}/candles.json"
        )

        params = {
            "interval": interval,
            "from": start.strftime("%Y-%m-%d"),
            "till": end.strftime("%Y-%m-%d"),
            "start": offset,
        }

        response = self.client.get(url, params=params)
        response.raise_for_status()

        payload = response.json()
        columns = payload["candles"]["columns"]
        rows = payload["candles"]["data"]

        result = []
        for row in rows:
            record = dict(zip(columns, row))

            result.append(
                CandleDTO(
                    ticker=ticker,
                    datetime=record["begin"],
                    open=record["open"],
                    high=record["high"],
                    low=record["low"],
                    close=record["close"],
                    volume=record["volume"],
                    interval=interval,
                )
            )

        return result
