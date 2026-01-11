from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

import pytest

from services.backfill import CandleBackfillService
from services.moex import MoexService
from storage.candle_storage import CandleStorage
from storage.security_storage import SecurityStorage
from schemas.candle import CandleDTO
from db.models import Candle, Security


class TestCandleBackfillService:
    """Test cases for CandleBackfillService"""

    def test_init(self):
        """Test CandleBackfillService initialization"""
        mock_moex = Mock(spec=MoexService)
        mock_candle_storage = Mock(spec=CandleStorage)
        mock_security_storage = Mock(spec=SecurityStorage)
        default_start = datetime(2024, 1, 1)

        service = CandleBackfillService(
            moex=mock_moex,
            candle_storage=mock_candle_storage,
            security_storage=mock_security_storage,
            interval=60,
            default_start=default_start,
        )

        assert service.moex == mock_moex
        assert service.candle_storage == mock_candle_storage
        assert service.security_storage == mock_security_storage
        assert service.interval == 60
        assert service.default_start == default_start

    def test_backfill_ticker_new_security(self):
        """Test backfilling ticker when security doesn't exist"""
        mock_moex = Mock(spec=MoexService)
        mock_candle_storage = Mock(spec=CandleStorage)
        mock_security_storage = Mock(spec=SecurityStorage)
        default_start = datetime(2024, 1, 1)

        # Mock security storage
        mock_security = Mock(spec=Security)
        mock_security_storage.get_or_create.return_value = mock_security

        # Mock candle storage - no existing candles
        mock_candle_storage.get_last_datetime.return_value = None

        # Mock MOEX response
        sample_candles = [
            CandleDTO(
                ticker="SBER",
                datetime=datetime(2024, 1, 1, 10, 0),
                open=50.0,
                high=51.0,
                low=49.0,
                close=50.5,
                volume=1000,
                interval=60,
            )
        ]
        mock_moex.fetch_candles.return_value = sample_candles

        # Mock candle storage upsert
        mock_candle_storage.upsert_many.return_value = 1

        service = CandleBackfillService(
            moex=mock_moex,
            candle_storage=mock_candle_storage,
            security_storage=mock_security_storage,
            interval=60,
            default_start=default_start,
        )

        service.backfill_ticker("SBER")

        # Verify security was created
        mock_security_storage.get_or_create.assert_called_once_with(ticker="SBER")

        # Verify last datetime was checked
        mock_candle_storage.get_last_datetime.assert_called_once_with(
            ticker="SBER", interval=60
        )

        # Verify candles were fetched from MOEX
        mock_moex.fetch_candles.assert_called_once()

        # Verify candles were inserted
        mock_candle_storage.upsert_many.assert_called_once()

    def test_backfill_ticker_existing_candles(self):
        """Test backfilling ticker when candles already exist"""
        mock_moex = Mock(spec=MoexService)
        mock_candle_storage = Mock(spec=CandleStorage)
        mock_security_storage = Mock(spec=SecurityStorage)
        default_start = datetime(2024, 1, 1)

        # Mock security storage
        mock_security = Mock(spec=Security)
        mock_security_storage.get_or_create.return_value = mock_security

        # Mock candle storage - existing candles
        last_datetime = datetime(2024, 1, 1, 15, 0)
        mock_candle_storage.get_last_datetime.return_value = last_datetime

        # Mock MOEX response
        sample_candles = [
            CandleDTO(
                ticker="SBER",
                datetime=datetime(2024, 1, 1, 16, 0),
                open=50.0,
                high=51.0,
                low=49.0,
                close=50.5,
                volume=1000,
                interval=60,
            )
        ]
        mock_moex.fetch_candles.return_value = sample_candles

        # Mock candle storage upsert
        mock_candle_storage.upsert_many.return_value = 1

        service = CandleBackfillService(
            moex=mock_moex,
            candle_storage=mock_candle_storage,
            security_storage=mock_security_storage,
            interval=60,
            default_start=default_start,
        )

        service.backfill_ticker("SBER")

        # Verify fetching started from last datetime
        call_args = mock_moex.fetch_candles.call_args
        assert call_args[1]["start"] == last_datetime

    def test_backfill_ticker_no_new_candles(self):
        """Test backfilling when no new candles are available"""
        mock_moex = Mock(spec=MoexService)
        mock_candle_storage = Mock(spec=CandleStorage)
        mock_security_storage = Mock(spec=SecurityStorage)
        default_start = datetime(2024, 1, 1)

        # Mock security storage
        mock_security = Mock(spec=Security)
        mock_security_storage.get_or_create.return_value = mock_security

        # Mock candle storage
        mock_candle_storage.get_last_datetime.return_value = None

        # Mock MOEX response - empty
        mock_moex.fetch_candles.return_value = []

        service = CandleBackfillService(
            moex=mock_moex,
            candle_storage=mock_candle_storage,
            security_storage=mock_security_storage,
            interval=60,
            default_start=default_start,
        )

        service.backfill_ticker("SBER")

        # Verify upsert was called with empty list
        mock_candle_storage.upsert_many.assert_called_once()

    def test_backfill_ticker_error_handling(self):
        """Test error handling during backfill"""
        mock_moex = Mock(spec=MoexService)
        mock_candle_storage = Mock(spec=CandleStorage)
        mock_security_storage = Mock(spec=SecurityStorage)
        default_start = datetime(2024, 1, 1)

        # Mock security storage
        mock_security = Mock(spec=Security)
        mock_security_storage.get_or_create.return_value = mock_security

        # Mock candle storage
        mock_candle_storage.get_last_datetime.return_value = None

        # Mock MOEX to raise exception
        mock_moex.fetch_candles.side_effect = Exception("MOEX API Error")

        service = CandleBackfillService(
            moex=mock_moex,
            candle_storage=mock_candle_storage,
            security_storage=mock_security_storage,
            interval=60,
            default_start=default_start,
        )

        # Should raise exception
        with pytest.raises(Exception, match="MOEX API Error"):
            service.backfill_ticker("SBER")

    def test_backfill_many_success(self):
        """Test backfilling multiple tickers successfully"""
        mock_moex = Mock(spec=MoexService)
        mock_candle_storage = Mock(spec=CandleStorage)
        mock_security_storage = Mock(spec=SecurityStorage)
        default_start = datetime(2024, 1, 1)

        # Mock security storage
        mock_security = Mock(spec=Security)
        mock_security_storage.get_or_create.return_value = mock_security

        # Mock candle storage
        mock_candle_storage.get_last_datetime.return_value = None
        mock_candle_storage.upsert_many.return_value = 1

        # Mock MOEX response
        sample_candles = [
            CandleDTO(
                ticker="SBER",
                datetime=datetime(2024, 1, 1, 10, 0),
                open=50.0,
                high=51.0,
                low=49.0,
                close=50.5,
                volume=1000,
                interval=60,
            )
        ]
        mock_moex.fetch_candles.return_value = sample_candles

        service = CandleBackfillService(
            moex=mock_moex,
            candle_storage=mock_candle_storage,
            security_storage=mock_security_storage,
            interval=60,
            default_start=default_start,
        )

        tickers = ["SBER", "GAZP"]
        service.backfill_many(tickers)

        # Verify each ticker was processed
        assert mock_security_storage.get_or_create.call_count == 2
        assert mock_moex.fetch_candles.call_count == 2
        assert mock_candle_storage.upsert_many.call_count == 2

    def test_backfill_many_with_errors(self):
        """Test backfilling multiple tickers with some errors"""
        mock_moex = Mock(spec=MoexService)
        mock_candle_storage = Mock(spec=CandleStorage)
        mock_security_storage = Mock(spec=SecurityStorage)
        default_start = datetime(2024, 1, 1)

        # Mock security storage
        mock_security = Mock(spec=Security)
        mock_security_storage.get_or_create.return_value = mock_security

        # Mock candle storage
        mock_candle_storage.get_last_datetime.return_value = None

        # Mock MOEX - success for first ticker, error for second
        sample_candles = [
            CandleDTO(
                ticker="SBER",
                datetime=datetime(2024, 1, 1, 10, 0),
                open=50.0,
                high=51.0,
                low=49.0,
                close=50.5,
                volume=1000,
                interval=60,
            )
        ]
        mock_moex.fetch_candles.side_effect = [sample_candles, Exception("MOEX Error")]

        mock_candle_storage.upsert_many.return_value = 1

        service = CandleBackfillService(
            moex=mock_moex,
            candle_storage=mock_candle_storage,
            security_storage=mock_security_storage,
            interval=60,
            default_start=default_start,
        )

        tickers = ["SBER", "GAZP"]

        # Should not raise exception, but handle errors gracefully
        service.backfill_many(tickers)

        # Verify both tickers were attempted
        assert mock_security_storage.get_or_create.call_count == 2
        assert mock_moex.fetch_candles.call_count == 2

    @patch("services.backfill.logger")
    def test_backfill_many_logging(self, mock_logger):
        """Test that errors are logged during backfill_many"""
        mock_moex = Mock(spec=MoexService)
        mock_candle_storage = Mock(spec=CandleStorage)
        mock_security_storage = Mock(spec=SecurityStorage)
        default_start = datetime(2024, 1, 1)

        # Mock security storage
        mock_security = Mock(spec=Security)
        mock_security_storage.get_or_create.return_value = mock_security

        # Mock candle storage
        mock_candle_storage.get_last_datetime.return_value = None

        # Mock MOEX to raise exception
        mock_moex.fetch_candles.side_effect = Exception("MOEX Error")

        service = CandleBackfillService(
            moex=mock_moex,
            candle_storage=mock_candle_storage,
            security_storage=mock_security_storage,
            interval=60,
            default_start=default_start,
        )

        service.backfill_many(["SBER"])

        # Verify error was logged
        mock_logger.error.assert_called_once()

    def test_candle_conversion(self):
        """Test conversion from CandleDTO to Candle model"""
        mock_moex = Mock(spec=MoexService)
        mock_candle_storage = Mock(spec=CandleStorage)
        mock_security_storage = Mock(spec=SecurityStorage)
        default_start = datetime(2024, 1, 1)

        # Mock security storage
        mock_security = Mock(spec=Security)
        mock_security_storage.get_or_create.return_value = mock_security

        # Mock candle storage
        mock_candle_storage.get_last_datetime.return_value = None

        # Mock MOEX response
        sample_candles = [
            CandleDTO(
                ticker="SBER",
                datetime=datetime(2024, 1, 1, 10, 0),
                open=50.0,
                high=51.0,
                low=49.0,
                close=50.5,
                volume=1000,
                interval=60,
            )
        ]
        mock_moex.fetch_candles.return_value = sample_candles

        service = CandleBackfillService(
            moex=mock_moex,
            candle_storage=mock_candle_storage,
            security_storage=mock_security_storage,
            interval=60,
            default_start=default_start,
        )

        service.backfill_ticker("SBER")

        # Verify candles were converted correctly
        call_args = mock_candle_storage.upsert_many.call_args[0][0]
        assert len(call_args) == 1

        candle = call_args[0]
        assert isinstance(candle, Candle)
        assert candle.ticker == "SBER"
        assert candle.datetime == datetime(2024, 1, 1, 10, 0)
        assert candle.open == 50.0
        assert candle.high == 51.0
        assert candle.low == 49.0
        assert candle.close == 50.5
        assert candle.volume == 1000
        assert candle.interval == 60
