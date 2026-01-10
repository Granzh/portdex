import pytest
from datetime import date
from portfolio.portfolio import Portfolio
from portfolio.position import Position
from schemas.trade import Trade, OperationType


class TestPortfolio:
    """Test cases for Portfolio class"""

    def test_init_empty_portfolio(self):
        """Test portfolio initialization"""
        portfolio = Portfolio()
        assert portfolio.positions == {}
        assert portfolio.cash == 0.0

    def test_apply_buy_trade_new_position(self, empty_portfolio, sample_trade_buy):
        """Test applying a buy trade for a new position"""
        empty_portfolio.apply_trade(sample_trade_buy)

        assert "SBER" in empty_portfolio.positions
        position = empty_portfolio.positions["SBER"]
        assert position.ticker == "SBER"
        assert position.quantity == 10
        assert position.cash_flow == -505.0  # - (50.0 * 10 + 5.0)

    def test_apply_buy_trade_existing_position(
        self, sample_portfolio, sample_trade_buy
    ):
        """Test applying a buy trade to an existing position"""
        initial_quantity = sample_portfolio.positions["SBER"].quantity
        initial_cash_flow = sample_portfolio.positions["SBER"].cash_flow

        sample_portfolio.apply_trade(sample_trade_buy)

        position = sample_portfolio.positions["SBER"]
        assert position.quantity == initial_quantity + 10
        assert position.cash_flow == initial_cash_flow - 505.0  # - (50.0 * 10 + 5.0)

    def test_apply_sell_trade_existing_position(
        self, sample_portfolio, sample_trade_sell
    ):
        """Test applying a sell trade to an existing position"""
        initial_quantity = sample_portfolio.positions["SBER"].quantity
        initial_cash_flow = sample_portfolio.positions["SBER"].cash_flow

        sample_portfolio.apply_trade(sample_trade_sell)

        position = sample_portfolio.positions["SBER"]
        assert position.quantity == initial_quantity - 5
        assert position.cash_flow == initial_cash_flow + 272.0  # 55.0 * 5 - 3.0

    def test_apply_sell_trade_insufficient_position(
        self, empty_portfolio, sample_trade_sell
    ):
        """Test applying a sell trade when position doesn't exist"""
        empty_portfolio.apply_trade(sample_trade_sell)

        assert "SBER" in empty_portfolio.positions
        position = empty_portfolio.positions["SBER"]
        assert position.ticker == "SBER"
        assert position.quantity == -5  # Negative quantity (short position)
        assert position.cash_flow == 272.0  # 55.0 * 5 - 3.0

    def test_apply_multiple_trades(self, empty_portfolio):
        """Test applying multiple trades in sequence"""
        buy_trade = Trade(
            ticker="GAZP",
            date=date(2024, 1, 1),
            price=150.0,
            quantity=20,
            fee=10.0,
            operation=OperationType.BUY,
        )
        sell_trade = Trade(
            ticker="GAZP",
            date=date(2024, 1, 2),
            price=160.0,
            quantity=10,
            fee=5.0,
            operation=OperationType.SELL,
        )

        empty_portfolio.apply_trade(buy_trade)
        empty_portfolio.apply_trade(sell_trade)

        position = empty_portfolio.positions["GAZP"]
        assert position.quantity == 10  # 20 bought - 10 sold
        assert position.cash_flow == -3010.0 + 1595.0  # -(150*20+10) + (160*10-5)

    def test_apply_different_tickers(self, empty_portfolio):
        """Test applying trades for different tickers"""
        trade_sber = Trade(
            ticker="SBER",
            date=date(2024, 1, 1),
            price=100.0,
            quantity=5,
            fee=5.0,
            operation=OperationType.BUY,
        )
        trade_gazp = Trade(
            ticker="GAZP",
            date=date(2024, 1, 1),
            price=150.0,
            quantity=3,
            fee=3.0,
            operation=OperationType.BUY,
        )

        empty_portfolio.apply_trade(trade_sber)
        empty_portfolio.apply_trade(trade_gazp)

        assert len(empty_portfolio.positions) == 2
        assert "SBER" in empty_portfolio.positions
        assert "GAZP" in empty_portfolio.positions
        assert empty_portfolio.positions["SBER"].quantity == 5
        assert empty_portfolio.positions["GAZP"].quantity == 3

    def test_zero_fee_trade(self, empty_portfolio):
        """Test applying trade with zero fee"""
        trade = Trade(
            ticker="SBER",
            date=date(2024, 1, 1),
            price=100.0,
            quantity=10,
            fee=0.0,
            operation=OperationType.BUY,
        )

        empty_portfolio.apply_trade(trade)

        position = empty_portfolio.positions["SBER"]
        assert position.quantity == 10
        assert position.cash_flow == -1000.0  # -100.0 * 10

    def test_large_quantity_trade(self, empty_portfolio):
        """Test applying trade with large quantity"""
        trade = Trade(
            ticker="SBER",
            date=date(2024, 1, 1),
            price=50.0,
            quantity=10000,
            fee=100.0,
            operation=OperationType.BUY,
        )

        empty_portfolio.apply_trade(trade)

        position = empty_portfolio.positions["SBER"]
        assert position.quantity == 10000
        assert position.cash_flow == -500100.0  # -(50.0 * 10000 + 100.0)
