import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from storage.candle_storage import CandleStorage
from schemas.candle import CandleDTO
from db.models import Candle


class TestCandleStorage:
    """Test cases for CandleStorage"""

    def test_init(self, mock_session):
        """Test CandleStorage initialization"""
        storage = CandleStorage(mock_session)
        assert storage.session == mock_session

    def test_upsert_many_empty_list(self, mock_session):
        """Test upserting empty list of candles"""
        storage = CandleStorage(mock_session)

        result = storage.upsert_many([])

        assert result == 0
        mock_session.execute.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_upsert_many_single_candle(self, mock_session):
        """Test upserting single candle"""
        storage = CandleStorage(mock_session)

        candle_dto = CandleDTO(
            ticker="SBER",
            datetime=datetime(2024, 1, 1, 10, 0),
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
            interval=60,
        )

        mock_result = Mock()
        mock_result.rowcount = 1
        mock_session.execute.return_value = mock_result

        result = storage.upsert_many([candle_dto])

        assert result == 1
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_upsert_many_multiple_candles(self, mock_session):
        """Test upserting multiple candles"""
        storage = CandleStorage(mock_session)

        candle_dtos = [
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
                ticker="GAZP",
                datetime=datetime(2024, 1, 1, 10, 0),
                open=150.0,
                high=151.0,
                low=149.0,
                close=150.5,
                volume=500,
                interval=60,
            ),
        ]

        mock_result = Mock()
        mock_result.rowcount = 2
        mock_session.execute.return_value = mock_result

        result = storage.upsert_many(candle_dtos)

        assert result == 2
        mock_session.execute.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_upsert_many_zero_rowcount(self, mock_session):
        """Test upsert when no rows are inserted"""
        storage = CandleStorage(mock_session)

        candle_dto = CandleDTO(
            ticker="SBER",
            datetime=datetime(2024, 1, 1, 10, 0),
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
            interval=60,
        )

        mock_result = Mock()
        mock_result.rowcount = 0
        mock_session.execute.return_value = mock_result

        result = storage.upsert_many([candle_dto])

        assert result == 0

    def test_upsert_many_none_rowcount(self, mock_session):
        """Test upsert when rowcount is None"""
        storage = CandleStorage(mock_session)

        candle_dto = CandleDTO(
            ticker="SBER",
            datetime=datetime(2024, 1, 1, 10, 0),
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
            interval=60,
        )

        mock_result = Mock()
        mock_result.rowcount = None
        mock_session.execute.return_value = mock_result

        result = storage.upsert_many([candle_dto])

        assert result == 0

    def test_get_last_datetime_success(self, mock_session):
        """Test getting last datetime successfully"""
        storage = CandleStorage(mock_session)

        last_datetime = datetime(2024, 1, 1, 15, 0)
        mock_session.execute.return_value.scalar_one_or_none.return_value = (
            last_datetime
        )

        result = storage.get_last_datetime(ticker="SBER", interval=60)

        assert result == last_datetime
        mock_session.execute.assert_called_once()

    def test_get_last_datetime_none(self, mock_session):
        """Test getting last datetime when none exists"""
        storage = CandleStorage(mock_session)

        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        result = storage.get_last_datetime(ticker="SBER", interval=60)

        assert result is None

    def test_get_last_datetime_different_parameters(self, mock_session):
        """Test getting last datetime with different parameters"""
        storage = CandleStorage(mock_session)

        last_datetime = datetime(2024, 1, 1, 15, 0)
        mock_session.execute.return_value.scalar_one_or_none.return_value = (
            last_datetime
        )

        result = storage.get_last_datetime(ticker="GAZP", interval=1)

        assert result == last_datetime
        mock_session.execute.assert_called_once()

    def test_get_candle_success(self, mock_session):
        """Test getting candle successfully"""
        storage = CandleStorage(mock_session)

        candle = Candle(
            ticker="SBER",
            datetime=datetime(2024, 1, 1, 10, 0),
            interval=60,
            open=50.0,
            high=51.0,
            low=49.0,
            close=50.5,
            volume=1000,
        )
        mock_session.execute.return_value.scalar_one_or_none.return_value = candle

        result = storage.get_candle(ticker="SBER", at=datetime(2024, 1, 1, 10, 0))

        assert result == candle
        assert result.ticker == "SBER"
        assert result.close == 50.5
        mock_session.execute.assert_called_once()

    def test_get_candle_not_found(self, mock_session):
        """Test getting candle when not found"""
        storage = CandleStorage(mock_session)

        mock_session.execute.return_value.scalar_one_or_none.return_value = None

        result = storage.get_candle(ticker="SBER", at=datetime(2024, 1, 1, 10, 0))

        assert result is None

    def test_get_candle_different_ticker(self, mock_session):
        """Test getting candle with different ticker"""
        storage = CandleStorage(mock_session)

        candle = Candle(
            ticker="GAZP",
            datetime=datetime(2024, 1, 1, 10, 0),
            interval=60,
            open=150.0,
            high=151.0,
            low=149.0,
            close=150.5,
            volume=500,
        )
        mock_session.execute.return_value.scalar_one_or_none.return_value = candle

        result = storage.get_candle(ticker="GAZP", at=datetime(2024, 1, 1, 10, 0))

        assert result == candle
        assert result.ticker == "GAZP"
