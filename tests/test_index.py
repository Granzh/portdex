import pytest
from datetime import datetime
from unittest.mock import Mock

from services.index import IndexService
from db.models import PortfolioSnapshot, PortfolioIndex


class TestIndexService:
    """Test cases for IndexService"""

    def test_init_default_base(self, mock_session):
        """Test IndexService initialization with default base"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        assert service.snapshot_storage == mock_snapshot_storage
        assert service.index_storage == mock_index_storage
        assert service.base == 1000.0

    def test_init_custom_base(self, mock_session):
        """Test IndexService initialization with custom base"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        service = IndexService(mock_snapshot_storage, mock_index_storage, base=500.0)

        assert service.base == 500.0

    def test_get_base_snapshot(self, mock_session):
        """Test fetching base snapshot"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        base_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 1), total_value=10000.0
        )
        mock_snapshot_storage.get_first.return_value = base_snapshot

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        result = service._get_base_snapshot()

        assert result == base_snapshot
        mock_snapshot_storage.get_first.assert_called_once()

    def test_get_base_snapshot_none(self, mock_session):
        """Test fetching base snapshot when none exists"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        mock_snapshot_storage.get_first.return_value = None

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        result = service._get_base_snapshot()

        assert result is None
        mock_snapshot_storage.get_first.assert_called_once()

    def test_calculate_and_save_success(self, mock_session):
        """Test successful index calculation and saving"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        base_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 1), total_value=10000.0
        )
        current_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 5), total_value=12000.0
        )

        mock_snapshot_storage.get_first.return_value = base_snapshot
        mock_index_storage.save.return_value = True

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        result = service.calculate_and_save(current_snapshot)

        assert result is True
        expected_index_value = (12000.0 / 10000.0) * 1000.0  # 1200.0
        mock_index_storage.save.assert_called_once()
        call_args = mock_index_storage.save.call_args[0][0]
        assert call_args.datetime == current_snapshot.datetime
        assert call_args.index_value == expected_index_value

    def test_calculate_and_save_no_base_snapshot(self, mock_session):
        """Test index calculation when no base snapshot exists"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        current_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 5), total_value=12000.0
        )
        mock_snapshot_storage.get_first.return_value = None

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        result = service.calculate_and_save(current_snapshot)

        assert result is False
        mock_index_storage.save.assert_not_called()

    def test_calculate_and_save_zero_base_value(self, mock_session):
        """Test index calculation when base value is zero"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        base_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 1), total_value=0.0
        )
        current_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 5), total_value=12000.0
        )

        mock_snapshot_storage.get_first.return_value = base_snapshot

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        result = service.calculate_and_save(current_snapshot)

        assert result is False
        mock_index_storage.save.assert_not_called()

    def test_calculate_and_save_custom_base(self, mock_session):
        """Test index calculation with custom base value"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        base_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 1), total_value=10000.0
        )
        current_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 5), total_value=12000.0
        )

        mock_snapshot_storage.get_first.return_value = base_snapshot
        mock_index_storage.save.return_value = True

        service = IndexService(mock_snapshot_storage, mock_index_storage, base=500.0)

        result = service.calculate_and_save(current_snapshot)

        assert result is True
        expected_index_value = (12000.0 / 10000.0) * 500.0  # 600.0
        call_args = mock_index_storage.save.call_args[0][0]
        assert call_args.index_value == expected_index_value

    def test_calculate_and_save_decrease_value(self, mock_session):
        """Test index calculation when portfolio value decreased"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        base_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 1), total_value=10000.0
        )
        current_snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 5), total_value=8000.0
        )

        mock_snapshot_storage.get_first.return_value = base_snapshot
        mock_index_storage.save.return_value = True

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        result = service.calculate_and_save(current_snapshot)

        assert result is True
        expected_index_value = (8000.0 / 10000.0) * 1000.0  # 800.0
        call_args = mock_index_storage.save.call_args[0][0]
        assert call_args.index_value == expected_index_value

    def test_backfill_success(self, mock_session):
        """Test successful backfill of portfolio index"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        snapshots = [
            PortfolioSnapshot(datetime=datetime(2024, 1, 1), total_value=10000.0),
            PortfolioSnapshot(datetime=datetime(2024, 1, 2), total_value=11000.0),
            PortfolioSnapshot(datetime=datetime(2024, 1, 3), total_value=12000.0),
        ]

        mock_snapshot_storage.get_all_ordered.return_value = snapshots
        mock_index_storage.save.return_value = True

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        service.backfill()

        # Should call save for each snapshot
        assert mock_index_storage.save.call_count == 3

        # Verify first call (base snapshot)
        first_call_args = mock_index_storage.save.call_args_list[0][0][0]
        assert first_call_args.datetime == datetime(2024, 1, 1)
        assert first_call_args.index_value == 1000.0  # (10000/10000) * 1000

        # Verify second call
        second_call_args = mock_index_storage.save.call_args_list[1][0][0]
        assert second_call_args.datetime == datetime(2024, 1, 2)
        assert second_call_args.index_value == 1100.0  # (11000/10000) * 1000

        # Verify third call
        third_call_args = mock_index_storage.save.call_args_list[2][0][0]
        assert third_call_args.datetime == datetime(2024, 1, 3)
        assert third_call_args.index_value == 1200.0  # (12000/10000) * 1000

    def test_backfill_empty_snapshots(self, mock_session):
        """Test backfill with no snapshots"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        mock_snapshot_storage.get_all_ordered.return_value = []

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        # This should raise an IndexError when trying to access snapshots[0]
        with pytest.raises(IndexError):
            service.backfill()

    def test_backfill_single_snapshot(self, mock_session):
        """Test backfill with only one snapshot"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        snapshots = [
            PortfolioSnapshot(datetime=datetime(2024, 1, 1), total_value=10000.0),
        ]

        mock_snapshot_storage.get_all_ordered.return_value = snapshots
        mock_index_storage.save.return_value = True

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        service.backfill()

        # Should call save once for the base snapshot
        assert mock_index_storage.save.call_count == 1
        call_args = mock_index_storage.save.call_args[0][0]
        assert call_args.datetime == datetime(2024, 1, 1)
        assert call_args.index_value == 1000.0  # (10000/10000) * 1000

    def test_backfill_with_custom_base(self, mock_session):
        """Test backfill with custom base value"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        snapshots = [
            PortfolioSnapshot(datetime=datetime(2024, 1, 1), total_value=10000.0),
            PortfolioSnapshot(datetime=datetime(2024, 1, 2), total_value=15000.0),
        ]

        mock_snapshot_storage.get_all_ordered.return_value = snapshots
        mock_index_storage.save.return_value = True

        service = IndexService(mock_snapshot_storage, mock_index_storage, base=500.0)

        service.backfill()

        # Verify base snapshot with custom base
        first_call_args = mock_index_storage.save.call_args_list[0][0][0]
        assert first_call_args.index_value == 500.0  # (10000/10000) * 500

        # Verify second snapshot with custom base
        second_call_args = mock_index_storage.save.call_args_list[1][0][0]
        assert second_call_args.index_value == 750.0  # (15000/10000) * 500

    def test_backfill_decreasing_values(self, mock_session):
        """Test backfill with decreasing portfolio values"""
        mock_snapshot_storage = Mock()
        mock_index_storage = Mock()

        snapshots = [
            PortfolioSnapshot(datetime=datetime(2024, 1, 1), total_value=10000.0),
            PortfolioSnapshot(datetime=datetime(2024, 1, 2), total_value=9000.0),
            PortfolioSnapshot(datetime=datetime(2024, 1, 3), total_value=8000.0),
        ]

        mock_snapshot_storage.get_all_ordered.return_value = snapshots
        mock_index_storage.save.return_value = True

        service = IndexService(mock_snapshot_storage, mock_index_storage)

        service.backfill()

        # Verify decreasing index values
        calls = mock_index_storage.save.call_args_list
        assert calls[0][0][0].index_value == 1000.0  # Base
        assert calls[1][0][0].index_value == 900.0  # (9000/10000) * 1000
        assert calls[2][0][0].index_value == 800.0  # (8000/10000) * 1000
