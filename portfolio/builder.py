import logging
from datetime import datetime

from db.models import PortfolioSnapshot, PortfolioSnapshotPosition
from portfolio.portfolio import Portfolio
from schemas.trade import OperationType, Trade
from storage.candle_storage import CandleStorage

logger = logging.getLogger(__name__)


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

            candle = self.candle_storage.get_last_before(ticker=pos.ticker, at=at)
            if candle is None:
                logger.warning("No candle for %s at %s", pos.ticker, at)
                continue
            total += pos.quantity * candle.close

        return total

    def snapshot(
        self,
        trades: list[Trade],
        at: datetime,
        prev_at: datetime | None,
    ) -> PortfolioSnapshot:
        """
        Builds a portfolio from a list of trades and calculates its value at a given time.
        cash_flow — приток/отток капитала ЗА ПЕРИОД (prev_at, at]
        """
        portfolio = Portfolio()
        cash_flow = 0.0

        for trade in sorted(trades, key=lambda t: t.date):
            trade_at = trade.date.replace(tzinfo=at.tzinfo)
            if trade_at > at:
                break

            portfolio.apply_trade(trade)

            if prev_at is not None and prev_at < trade.date <= at:
                candle = self.candle_storage.get_last_before(
                    ticker=trade.ticker, at=trade_at
                )

                if candle is None:
                    logger.warning("No candle for %s at %s", trade.ticker, trade_at)
                    continue

                sign = 1 if trade.operation == OperationType.BUY else -1
                cash_flow += sign * candle.close * trade.quantity
                cash_flow += trade.fee

        total_value = self.valuate(portfolio, at)

        snapshot = PortfolioSnapshot(
            datetime=at,
            total_value=total_value,
            cash_flow=cash_flow,
        )

        snapshot.positions = [
            PortfolioSnapshotPosition(
                ticker=pos.ticker,
                quantity=pos.quantity,
            )
            for pos in portfolio.positions.values()
            if pos.quantity != 0
        ]

        return snapshot
