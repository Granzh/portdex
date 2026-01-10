from datetime import datetime

from db.models import PortfolioSnapshot
from portfolio.portfolio import Portfolio
from schemas.trade import Trade
from storage.candle_storage import CandleStorage


class PortfolioBuilder:
    """
    Builds a portfolio from a list of trades.
    """

    def __init__(self, candle_storage: CandleStorage):
        self.candle_storage = candle_storage

    def build(self, trades: list[Trade], at: datetime) -> Portfolio:
        """
        Builds a portfolio from a list of trades.
        """
        portfolio = Portfolio()

        for trade in sorted(trades, key=lambda t: t.date):
            if trade.date > at.date():
                break

            portfolio.apply_trade(trade)

        return portfolio

    def valuate(self, portfolio: Portfolio, at: datetime) -> float:
        """
        Calculates the value of a portfolio at a given time.
        """
        total = 0.0

        for pos in portfolio.positions.values():
            if pos.quantity == 0:
                continue

            candle = self.candle_storage.get_candle(ticker=pos.ticker, at=at)
            if candle is None:
                continue
            total += pos.quantity * candle.close

        return total

    def snapshot(self, trades: list[Trade], at: datetime) -> PortfolioSnapshot:
        """
        Builds a portfolio from a list of trades and calculates its value at a given time.
        """
        portfolio = self.build(trades, at)
        value = self.valuate(portfolio, at)

        return PortfolioSnapshot(datetime=at, total_value=value)
