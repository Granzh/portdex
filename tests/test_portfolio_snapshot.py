from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from schemas.trade import OperationType, Trade
from services.portfolio_snapshot import PortfolioSnapshotService


class TestPortfolioSnapshotService:
    """Test cases for PortfolioSnapshotService"""

    def test_init(self):
        """Test PortfolioSnapshotService initialization"""
        mock_sheets = Mock()
        mock_builder = Mock()
        mock_storage = Mock()

        service = PortfolioSnapshotService(mock_sheets, mock_builder, mock_storage)

        assert service.sheets == mock_sheets
        assert service.builder == mock_builder
        assert service.storage == mock_storage

    def test_take_snapshot_with_default_time(self):
        """Test taking snapshot with default current time"""
        mock_sheets = Mock()
        mock_builder = Mock()
        mock_storage = Mock()

        # Mock trades from sheets
        trades = [
            Trade(
                ticker="SBER",
                date="2024-01-01",
                price=50.0,
                quantity=10,
                operation=OperationType.BUY,
            ),
        ]
        mock_sheets.fetch_trades.return_value = trades

        # Mock builder snapshot
        mock_snapshot = Mock()
        mock_builder.snapshot.return_value = mock_snapshot

        # Mock storage save
        mock_storage.save.return_value = True

        service = PortfolioSnapshotService(mock_sheets, mock_builder, mock_storage)

        with patch("services.portfolio_snapshot.datetime") as mock_datetime:
            now = datetime(2024, 1, 5, 12, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = now

            result = service.take_snapshot()

            assert result is True
            mock_sheets.fetch_trades.assert_called_once()
            mock_builder.snapshot.assert_called_once_with(trades, now)
            mock_storage.save.assert_called_once_with(mock_snapshot)

    def test_take_snapshot_with_custom_time(self):
        """Test taking snapshot with custom time"""
        mock_sheets = Mock()
        mock_builder = Mock()
        mock_storage = Mock()

        trades = [
            Trade(
                ticker="SBER",
                date="2024-01-01",
                price=50.0,
                quantity=10,
                operation=OperationType.BUY,
            ),
        ]
        mock_sheets.fetch_trades.return_value = trades

        mock_snapshot = Mock()
        mock_builder.snapshot.return_value = mock_snapshot
        mock_storage.save.return_value = True

        custom_time = datetime(2024, 1, 10, 15, 30)

        service = PortfolioSnapshotService(mock_sheets, mock_builder, mock_storage)

        result = service.take_snapshot(at=custom_time)

        assert result is True
        mock_sheets.fetch_trades.assert_called_once()
        mock_builder.snapshot.assert_called_once_with(trades, custom_time)
        mock_storage.save.assert_called_once_with(mock_snapshot)

    def test_take_snapshot_with_empty_trades(self):
        """Test taking snapshot when no trades are returned"""
        mock_sheets = Mock()
        mock_builder = Mock()
        mock_storage = Mock()

        mock_sheets.fetch_trades.return_value = []

        mock_snapshot = Mock()
        mock_builder.snapshot.return_value = mock_snapshot
        mock_storage.save.return_value = True

        custom_time = datetime(2024, 1, 10, 15, 30)

        service = PortfolioSnapshotService(mock_sheets, mock_builder, mock_storage)

        result = service.take_snapshot(at=custom_time)

        assert result is True
        mock_sheets.fetch_trades.assert_called_once()
        mock_builder.snapshot.assert_called_once_with([], custom_time)
        mock_storage.save.assert_called_once_with(mock_snapshot)

    def test_take_snapshot_storage_save_failure(self):
        """Test taking snapshot when storage save fails"""
        mock_sheets = Mock()
        mock_builder = Mock()
        mock_storage = Mock()

        trades = [
            Trade(
                ticker="SBER",
                date="2024-01-01",
                price=50.0,
                quantity=10,
                operation=OperationType.BUY,
            ),
        ]
        mock_sheets.fetch_trades.return_value = trades

        mock_snapshot = Mock()
        mock_builder.snapshot.return_value = mock_snapshot
        mock_storage.save.return_value = False  # Save failed

        custom_time = datetime(2024, 1, 10, 15, 30)

        service = PortfolioSnapshotService(mock_sheets, mock_builder, mock_storage)

        result = service.take_snapshot(at=custom_time)

        assert result is False
        mock_sheets.fetch_trades.assert_called_once()
        mock_builder.snapshot.assert_called_once_with(trades, custom_time)
        mock_storage.save.assert_called_once_with(mock_snapshot)

    def test_take_snapshot_with_multiple_trades(self):
        """Test taking snapshot with multiple trades"""
        mock_sheets = Mock()
        mock_builder = Mock()
        mock_storage = Mock()

        trades = [
            Trade(
                ticker="SBER",
                date="2024-01-01",
                price=50.0,
                quantity=10,
                operation=OperationType.BUY,
            ),
            Trade(
                ticker="GAZP",
                date="2024-01-02",
                price=150.0,
                quantity=5,
                operation=OperationType.BUY,
            ),
            Trade(
                ticker="SBER",
                date="2024-01-03",
                price=55.0,
                quantity=5,
                operation=OperationType.SELL,
            ),
        ]
        mock_sheets.fetch_trades.return_value = trades

        mock_snapshot = Mock()
        mock_builder.snapshot.return_value = mock_snapshot
        mock_storage.save.return_value = True

        custom_time = datetime(2024, 1, 10, 15, 30)

        service = PortfolioSnapshotService(mock_sheets, mock_builder, mock_storage)

        result = service.take_snapshot(at=custom_time)

        assert result is True
        mock_sheets.fetch_trades.assert_called_once()
        mock_builder.snapshot.assert_called_once_with(trades, custom_time)
        mock_storage.save.assert_called_once_with(mock_snapshot)

    def test_take_snapshot_handles_sheets_exception(self):
        """Test taking snapshot when Google Sheets service throws exception"""
        mock_sheets = Mock()
        mock_builder = Mock()
        mock_storage = Mock()

        # Mock sheets to raise exception
        mock_sheets.fetch_trades.side_effect = Exception("Google Sheets API error")

        custom_time = datetime(2024, 1, 10, 15, 30)

        service = PortfolioSnapshotService(mock_sheets, mock_builder, mock_storage)

        # Should propagate the exception
        with pytest.raises(Exception, match="Google Sheets API error"):
            service.take_snapshot(at=custom_time)

        mock_sheets.fetch_trades.assert_called_once()
        mock_builder.snapshot.assert_not_called()
        mock_storage.save.assert_not_called()

    def test_take_snapshot_handles_builder_exception(self):
        """Test taking snapshot when builder throws exception"""
        mock_sheets = Mock()
        mock_builder = Mock()
        mock_storage = Mock()

        trades = [
            Trade(
                ticker="SBER",
                date="2024-01-01",
                price=50.0,
                quantity=10,
                operation=OperationType.BUY,
            ),
        ]
        mock_sheets.fetch_trades.return_value = trades

        # Mock builder to raise exception
        mock_builder.snapshot.side_effect = Exception("Builder error")

        custom_time = datetime(2024, 1, 10, 15, 30)

        service = PortfolioSnapshotService(mock_sheets, mock_builder, mock_storage)

        # Should propagate the exception
        with pytest.raises(Exception, match="Builder error"):
            service.take_snapshot(at=custom_time)

        mock_sheets.fetch_trades.assert_called_once()
        mock_builder.snapshot.assert_called_once_with(trades, custom_time)
        mock_storage.save.assert_not_called()
