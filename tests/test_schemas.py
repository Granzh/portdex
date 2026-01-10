import pytest
from datetime import datetime, date
from pydantic import ValidationError

from schemas.candle import CandleDTO
from schemas.trade import Trade, OperationType
from schemas.index_point import IndexPoint
from schemas.portfolio_state import PortfolioState


class TestCandleDTO:
    """Test cases for CandleDTO"""

    def test_valid_candle_dto(self):
        """Test creating a valid CandleDTO"""
        candle = CandleDTO(
            ticker="SBER",
            datetime=datetime(2024, 1, 1, 10, 0),
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
            interval=60,
        )

        assert candle.ticker == "SBER"
        assert candle.datetime == datetime(2024, 1, 1, 10, 0)
        assert candle.open == 50.0
        assert candle.high == 51.0
        assert candle.low == 49.0
        assert candle.close == 50.5
        assert candle.volume == 1000
        assert candle.interval == 60

    def test_candle_dto_zero_values(self):
        """Test CandleDTO with zero values"""
        candle = CandleDTO(
            ticker="GAZP",
            datetime=datetime(2024, 1, 1, 10, 0),
            open=0.0,
            high=0.0,
            low=0.0,
            close=0.0,
            volume=0,
            interval=60,
        )

        assert candle.volume == 0
        assert candle.open == 0.0

    def test_candle_dto_negative_volume(self):
        """Test CandleDTO with negative volume (should be allowed)"""
        candle = CandleDTO(
            ticker="SBER",
            datetime=datetime(2024, 1, 1, 10, 0),
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=-100,  # Should be allowed
            interval=60,
        )

        assert candle.volume == -100

    def test_candle_dto_model_dump(self):
        """Test CandleDTO model_dump method"""
        candle = CandleDTO(
            ticker="SBER",
            datetime=datetime(2024, 1, 1, 10, 0),
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
            interval=60,
        )

        data = candle.model_dump()
        assert data["ticker"] == "SBER"
        assert data["open"] == 50.0
        assert data["volume"] == 1000


class TestTrade:
    """Test cases for Trade"""

    def test_valid_buy_trade(self):
        """Test creating a valid buy trade"""
        trade = Trade(
            ticker="SBER",
            date=date(2024, 1, 1),
            price=50.0,
            quantity=100,
            fee=5.0,
            operation=OperationType.BUY,
        )

        assert trade.ticker == "SBER"
        assert trade.date == date(2024, 1, 1)
        assert trade.price == 50.0
        assert trade.quantity == 100
        assert trade.fee == 5.0
        assert trade.operation == OperationType.BUY

    def test_valid_sell_trade(self):
        """Test creating a valid sell trade"""
        trade = Trade(
            ticker="GAZP",
            date=date(2024, 1, 2),
            price=150.0,
            quantity=50,
            fee=3.0,
            operation=OperationType.SELL,
        )

        assert trade.operation == OperationType.SELL

    def test_trade_with_default_fee(self):
        """Test trade with default fee value"""
        trade = Trade(
            ticker="SBER",
            date=date(2024, 1, 1),
            price=50.0,
            quantity=100,
            operation=OperationType.BUY,
        )

        assert trade.fee == 0.0

    def test_trade_zero_quantity(self):
        """Test trade with zero quantity"""
        trade = Trade(
            ticker="SBER",
            date=date(2024, 1, 1),
            price=50.0,
            quantity=0,
            operation=OperationType.BUY,
        )

        assert trade.quantity == 0

    def test_trade_negative_price(self):
        """Test trade with negative price (should be allowed)"""
        trade = Trade(
            ticker="SBER",
            date=date(2024, 1, 1),
            price=-50.0,
            quantity=100,
            operation=OperationType.BUY,
        )

        assert trade.price == -50.0

    def test_trade_negative_quantity(self):
        """Test trade with negative quantity (should be allowed)"""
        trade = Trade(
            ticker="SBER",
            date=date(2024, 1, 1),
            price=50.0,
            quantity=-100,
            operation=OperationType.BUY,
        )

        assert trade.quantity == -100

    def test_trade_negative_fee(self):
        """Test trade with negative fee (rebate)"""
        trade = Trade(
            ticker="SBER",
            date=date(2024, 1, 1),
            price=50.0,
            quantity=100,
            fee=-5.0,
            operation=OperationType.BUY,
        )

        assert trade.fee == -5.0


# Test for IndexPoint
try:
    from schemas.index_point import IndexPoint

    class TestIndexPoint:
        """Test cases for IndexPoint"""

        def test_valid_index_point(self):
            """Test creating a valid IndexPoint"""
            index_point = IndexPoint(datetime=datetime(2024, 1, 1, 10, 0), value=1000.5)

            assert index_point.datetime == datetime(2024, 1, 1, 10, 0)
            assert index_point.value == 1000.5

except ImportError:
    # IndexPoint schema doesn't exist, skip tests
    pass


# Test for PortfolioState
try:
    from schemas.portfolio_state import PortfolioState

    class TestPortfolioState:
        """Test cases for PortfolioState"""

        def test_valid_portfolio_state(self):
            """Test creating a valid PortfolioState"""
            portfolio_state = PortfolioState(
                datetime=datetime(2024, 1, 1, 10, 0),
                positions={"SBER": 50000.0, "GAZP": 35000.0},
                total_value=100000.0,
            )

            assert portfolio_state.datetime == datetime(2024, 1, 1, 10, 0)
            assert portfolio_state.positions == {"SBER": 50000.0, "GAZP": 35000.0}
            assert portfolio_state.total_value == 100000.0

except ImportError:
    # PortfolioState schema doesn't exist, skip tests
    pass


class TestOperationType:
    """Test cases for OperationType enum"""

    def test_operation_type_values(self):
        """Test OperationType enum values"""
        assert OperationType.BUY == "BUY"
        assert OperationType.SELL == "SELL"
        assert OperationType.BUY.value == "BUY"
        assert OperationType.SELL.value == "SELL"

    def test_operation_type_iteration(self):
        """Test iterating through OperationType values"""
        operations = list(OperationType)
        assert OperationType.BUY in operations
        assert OperationType.SELL in operations
        assert len(operations) == 2
