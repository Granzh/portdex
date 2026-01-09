from datetime import datetime

from db.models import PortfolioSnapshot
from portfolio.portfolio import Portfolio
from schemas.trade import Trade
from storage.candle_storage import CandleStorage


class PortfolioBuilder:
    def __init__(self, candle_storage: CandleStorage):
        self.candle_storage = candle_storage

    def build(self, trades: list[Trade], at: datetime) -> Portfolio:
        portfolio = Portfolio()

        for trade in sorted(trades, key=lambda t: t.date):
            if trade.date > at.date():
                break

            portfolio.apply_trade(trade)

        return portfolio

    def valuate(self, portfolio: Portfolio, at: datetime) -> float:
        total = 0.0

        for pos in portfolio.positions.values():
            if pos.quantity == 0:
                continue

            candle = self.candle_storage.get_candle(ticker=pos.ticker, at=at)
            total += pos.quantity * candle.close

        return total

    def snapshot(self, trades: list[Trade], at: datetime) -> PortfolioSnapshot:
        portfolio = self.build(trades, at)
        value = self.valuate(portfolio, at)

        return PortfolioSnapshot(portfolio=portfolio, value=value)
