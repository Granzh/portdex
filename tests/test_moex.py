from datetime import datetime

from services.moex import MoexService


def test_fetch_candles_smoke():
    service = MoexService()

    candles = service.fetch_candles(
        ticker="SBER", interval=60, start=datetime(2024, 1, 1), end=datetime(2024, 1, 2)
    )

    assert candles
    assert candles[0].open > 0
