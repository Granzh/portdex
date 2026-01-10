import pytest
from datetime import datetime, date
from unittest.mock import Mock, MagicMock
from portfolio.position import Position
from portfolio.portfolio import Portfolio
from schemas.candle import CandleDTO
from schemas.trade import Trade, OperationType


@pytest.fixture
def sample_position():
    """Sample position fixture"""
    return Position(ticker="SBER", quantity=100, cash_flow=-5000.0)


@pytest.fixture
def empty_portfolio():
    """Empty portfolio fixture"""
    return Portfolio()


@pytest.fixture
def sample_portfolio():
    """Portfolio with sample positions"""
    portfolio = Portfolio()
    portfolio.positions["SBER"] = Position("SBER", 100, -5000.0)
    portfolio.positions["GAZP"] = Position("GAZP", 200, -8000.0)
    portfolio.cash = 15000.0
    return portfolio


@pytest.fixture
def sample_trade_buy():
    """Sample buy trade fixture"""
    return Trade(
        ticker="SBER",
        date=date(2024, 1, 1),
        price=50.0,
        quantity=10,
        fee=5.0,
        operation=OperationType.BUY,
    )


@pytest.fixture
def sample_trade_sell():
    """Sample sell trade fixture"""
    return Trade(
        ticker="SBER",
        date=date(2024, 1, 2),
        price=55.0,
        quantity=5,
        fee=3.0,
        operation=OperationType.SELL,
    )


@pytest.fixture
def sample_candles():
    """Sample candles fixture"""
    return [
        CandleDTO(
            ticker="SBER",
            datetime=datetime(2024, 1, 1, 10, 0),
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
            interval=60,
        ),
        CandleDTO(
            ticker="SBER",
            datetime=datetime(2024, 1, 1, 11, 0),
            open=50.5,
            high=52.0,
            low=50.0,
            close=51.5,
            volume=1200,
            interval=60,
        ),
    ]


@pytest.fixture
def mock_http_client():
    """Mock HTTP client fixture"""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_client.get.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_moex_response_data():
    """Mock MOEX API response data"""
    return {
        "candles": {
            "columns": ["begin", "open", "high", "low", "close", "volume"],
            "data": [
                [datetime(2024, 1, 1, 10, 0), 50.0, 51.0, 49.0, 50.5, 1000],
                [datetime(2024, 1, 1, 11, 0), 50.5, 52.0, 50.0, 51.5, 1200],
            ],
        }
    }


@pytest.fixture
def mock_session():
    """Mock SQLAlchemy session fixture"""
    return Mock()


@pytest.fixture
def mock_candle_storage():
    """Mock candle storage fixture"""
    return Mock()


@pytest.fixture
def mock_services():
    """Mock services fixture"""
    return {
        "backfill_service": Mock(),
        "snapshot_service": Mock(),
        "index_service": Mock(),
    }
