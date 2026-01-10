from datetime import date, datetime
from unittest.mock import Mock

import pytest

from db.models import Candle, PortfolioSnapshot
from portfolio.builder import PortfolioBuilder
from portfolio.portfolio import Portfolio
from portfolio.position import Position
from schemas.candle import CandleDTO
from schemas.trade import OperationType, Trade


class TestPortfolioBuilder:
    """Test cases for PortfolioBuilder"""

    def test_init(self, mock_candle_storage):
        """Test PortfolioBuilder initialization"""
        builder = PortfolioBuilder(mock_candle_storage)
        assert builder.candle_storage == mock_candle_storage

    def test_build_empty_trades(self, mock_candle_storage):
        """Test building portfolio from empty trades list"""
        builder = PortfolioBuilder(mock_candle_storage)
        at = datetime(2024, 1, 1, 12, 0)

        portfolio = builder.build([], at)

        assert isinstance(portfolio, Portfolio)
        assert portfolio.positions == {}
        assert portfolio.cash == 0.0

    def test_build_trades_before_target_date(self, mock_candle_storage):
        """Test building portfolio with trades before target date"""
        builder = PortfolioBuilder(mock_candle_storage)
        at = datetime(2024, 1, 5, 12, 0)

        trades = [
            Trade(
                ticker="SBER",
                date=date(2024, 1, 1),
                price=50.0,
                quantity=10,
                operation=OperationType.BUY,
            ),
            Trade(
                ticker="GAZP",
                date=date(2024, 1, 3),
                price=150.0,
                quantity=5,
                operation=OperationType.BUY,
            ),
        ]

        portfolio = builder.build(trades, at)

        assert len(portfolio.positions) == 2
        assert "SBER" in portfolio.positions
        assert "GAZP" in portfolio.positions
        assert portfolio.positions["SBER"].quantity == 10
        assert portfolio.positions["GAZP"].quantity == 5

    def test_build_trades_after_target_date(self, mock_candle_storage):
        """Test building portfolio with trades after target date"""
        builder = PortfolioBuilder(mock_candle_storage)
        at = datetime(2024, 1, 5, 12, 0)

        trades = [
            Trade(
                ticker="SBER",
                date=date(2024, 1, 6),
                price=50.0,
                quantity=10,
                operation=OperationType.BUY,
            ),
            Trade(
                ticker="GAZP",
                date=date(2024, 1, 10),
                price=150.0,
                quantity=5,
                operation=OperationType.BUY,
            ),
        ]

        portfolio = builder.build(trades, at)

        assert portfolio.positions == {}
        assert portfolio.cash == 0.0

    def test_build_mixed_date_trades(self, mock_candle_storage):
        """Test building portfolio with mixed date trades"""
        builder = PortfolioBuilder(mock_candle_storage)
        at = datetime(2024, 1, 5, 12, 0)

        trades = [
            Trade(
                ticker="SBER",
                date=date(2024, 1, 1),
                price=50.0,
                quantity=10,
                operation=OperationType.BUY,
            ),
            Trade(
                ticker="GAZP",
                date=date(2024, 1, 6),
                price=150.0,
                quantity=5,
                operation=OperationType.BUY,
            ),
            Trade(
                ticker="SBER",
                date=date(2024, 1, 3),
                price=55.0,
                quantity=5,
                operation=OperationType.BUY,
            ),
            Trade(
                ticker="GAZP",
                date=date(2024, 1, 7),
                price=155.0,
                quantity=2,
                operation=OperationType.BUY,
            ),
        ]

        portfolio = builder.build(trades, at)

        # Only trades before or on target date should be applied
        assert (
            len(portfolio.positions) == 1
        )  # Only SBER (GAZP trades are after target date)
        assert portfolio.positions["SBER"].quantity == 15  # 10 + 5

    def test_build_trades_sorted_by_date(self, mock_candle_storage):
        """Test that trades are applied in chronological order"""
        builder = PortfolioBuilder(mock_candle_storage)
        at = datetime(2024, 1, 10, 12, 0)

        trades = [
            Trade(
                ticker="SBER",
                date=date(2024, 1, 5),
                price=60.0,
                quantity=5,
                operation=OperationType.SELL,
            ),
            Trade(
                ticker="SBER",
                date=date(2024, 1, 1),
                price=50.0,
                quantity=20,
                operation=OperationType.BUY,
            ),
        ]

        portfolio = builder.build(trades, at)

        # Should buy first, then sell
        position = portfolio.positions["SBER"]
        assert position.quantity == 15  # 20 bought - 5 sold
        # cash_flow should reflect buy then sell: -(50*20) + (60*5) = -1000 + 300 = -700
        assert position.cash_flow == -700.0

    def test_valuate_empty_portfolio(self, mock_candle_storage):
        """Test valuating empty portfolio"""
        builder = PortfolioBuilder(mock_candle_storage)
        portfolio = Portfolio()
        at = datetime(2024, 1, 1, 12, 0)

        value = builder.valuate(portfolio, at)

        assert value == 0.0

    def test_valuate_portfolio_with_zero_quantity_positions(self, mock_candle_storage):
        """Test valuating portfolio with zero quantity positions"""
        builder = PortfolioBuilder(mock_candle_storage)
        portfolio = Portfolio()
        portfolio.positions["SBER"] = Position("SBER", 0, 0.0)
        at = datetime(2024, 1, 1, 12, 0)

        value = builder.valuate(portfolio, at)

        assert value == 0.0

    def test_valuate_portfolio_with_valid_candles(self, mock_candle_storage):
        """Test valuating portfolio with available candle data"""
        builder = PortfolioBuilder(mock_candle_storage)
        portfolio = Portfolio()
        portfolio.positions["SBER"] = Position("SBER", 10, -500.0)
        portfolio.positions["GAZP"] = Position("GAZP", 5, -750.0)

        at = datetime(2024, 1, 1, 12, 0)

        candle_sber = Candle(
            ticker="SBER",
            datetime=at,
            interval=60,
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
        )
        candle_gazp = Candle(
            ticker="GAZP",
            datetime=at,
            interval=60,
            open=150.0,
            high=151.0,
            low=149.0,
            close=150.5,
            volume=500,
        )
        candle_gazp = Candle(ticker="GAZP", datetime=at, interval=60, open=150.0, high=151.0, low=149.0, close=150.5, volume=500)

        def mock_get_candle(ticker, **kwargs):
            if ticker == "SBER":
                return candle_sber
            elif ticker == "GAZP":
                return candle_gazp
            return None

        mock_candle_storage.get_candle.side_effect = mock_get_candle

        value = builder.valuate(portfolio, at)

        expected_value = 10 * 50.5 + 5 * 150.5  # 505 + 752.5 = 1257.5
        assert value == expected_value

    def test_valuate_portfolio_with_missing_candles(self, mock_candle_storage):
        """Test valuating portfolio when some candles are missing"""
        builder = PortfolioBuilder(mock_candle_storage)
        portfolio = Portfolio()
        portfolio.positions["SBER"] = Position("SBER", 10, -500.0)
        portfolio.positions["GAZP"] = Position("GAZP", 5, -750.0)

        at = datetime(2024, 1, 1, 12, 0)

        # Mock candle storage to return None for GAZP
        candle_sber = Candle(
            ticker="SBER",
            datetime=at,
            interval=60,
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
        )
        mock_candle_storage.get_candle.side_effect = (
            lambda ticker, **kwargs: candle_sber if ticker == "SBER" else None
        )

        value = builder.valuate(portfolio, at)

        # Only SBER should be valued
        expected_value = 10 * 50.5  # 505
        assert value == expected_value

    def test_snapshot(self, mock_candle_storage):
        """Test creating portfolio snapshot"""
        builder = PortfolioBuilder(mock_candle_storage)

        trades = [
            Trade(
                ticker="SBER",
                date=date(2024, 1, 1),
                price=50.0,
                quantity=10,
                operation=OperationType.BUY,
            ),
        ]
        at = datetime(2024, 1, 5, 12, 0)

        # Mock candle storage
        candle = Candle(
            ticker="SBER",
            datetime=at,
            interval=60,
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
        )
        mock_candle_storage.get_candle.return_value = candle

        snapshot = builder.snapshot(trades, at)

        assert snapshot.datetime == at
        assert snapshot.total_value == 10 * 50.5  # quantity * close price

    def test_snapshot_with_empty_portfolio(self, mock_candle_storage):
        """Test creating snapshot with empty trades"""
        builder = PortfolioBuilder(mock_candle_storage)

        trades = []
        at = datetime(2024, 1, 5, 12, 0)

        snapshot = builder.snapshot(trades, at)

        assert snapshot.datetime == at
        assert snapshot.total_value == 0.0

    def test_valuate_negative_quantities(self, mock_candle_storage):
        """Test valuating portfolio with negative quantities (short positions)"""
        builder = PortfolioBuilder(mock_candle_storage)
        portfolio = Portfolio()
        portfolio.positions["SBER"] = Position("SBER", -5, 250.0)  # Short position

        at = datetime(2024, 1, 1, 12, 0)

        candle = Candle(
            ticker="SBER",
            datetime=at,
            interval=60,
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
        )
        mock_candle_storage.get_candle.return_value = candle

        value = builder.valuate(portfolio, at)

        # Negative quantity should still be valued (typically short positions have negative value)
        expected_value = -5 * 50.5  # -252.5
        assert value == expected_value
