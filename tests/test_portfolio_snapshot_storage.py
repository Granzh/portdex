import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock
from sqlalchemy.exc import SQLAlchemyError

from storage.portfolio_snapshot_storage import PortfolioSnapshotStorage
from db.models import PortfolioSnapshot


class TestPortfolioSnapshotStorage:
    """Test cases for PortfolioSnapshotStorage"""

    def test_init(self, mock_session):
        """Test PortfolioSnapshotStorage initialization"""
        storage = PortfolioSnapshotStorage(mock_session)
        assert storage.session == mock_session

    def test_save_success(self, mock_session):
        """Test successful save of portfolio snapshot"""
        storage = PortfolioSnapshotStorage(mock_session)

        snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 1, 12, 0), total_value=10000.0
        )

        result = storage.save(snapshot)

        assert result is True
        mock_session.add.assert_called_once_with(snapshot)
        mock_session.commit.assert_called_once()

    def test_save_failure_rollback(self, mock_session):
        """Test save failure with rollback"""
        storage = PortfolioSnapshotStorage(mock_session)

        snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 1, 12, 0), total_value=10000.0
        )

        # Mock commit to raise exception
        mock_session.commit.side_effect = SQLAlchemyError("Database error")

        result = storage.save(snapshot)

        assert result is False
        mock_session.add.assert_called_once_with(snapshot)
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_called_once()

    def test_get_first_success(self, mock_session):
        """Test getting first portfolio snapshot successfully"""
        storage = PortfolioSnapshotStorage(mock_session)

        snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 1, 12, 0), total_value=10000.0
        )
        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = snapshot
        mock_session.query.return_value = mock_query

        result = storage.get_first()

        assert result == snapshot
        mock_session.query.assert_called_once_with(PortfolioSnapshot)
        mock_query.order_by.assert_called_once()

    def test_get_first_none(self, mock_session):
        """Test getting first portfolio snapshot when none exists"""
        storage = PortfolioSnapshotStorage(mock_session)

        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_session.query.return_value = mock_query

        result = storage.get_first()

        assert result is None

    def test_get_last_success(self, mock_session):
        """Test getting last portfolio snapshot successfully"""
        storage = PortfolioSnapshotStorage(mock_session)

        snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 2, 12, 0), total_value=12000.0
        )
        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = snapshot
        mock_session.query.return_value = mock_query

        result = storage.get_last()

        assert result == snapshot
        mock_session.query.assert_called_once_with(PortfolioSnapshot)
        mock_query.order_by.assert_called_once()

    def test_get_last_none(self, mock_session):
        """Test getting last portfolio snapshot when none exists"""
        storage = PortfolioSnapshotStorage(mock_session)

        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None
        mock_session.query.return_value = mock_query

        result = storage.get_last()

        assert result is None

    def test_get_all_ordered_success(self, mock_session):
        """Test getting all portfolio snapshots ordered successfully"""
        storage = PortfolioSnapshotStorage(mock_session)

        snapshots = [
            PortfolioSnapshot(
                datetime=datetime(2024, 1, 1, 12, 0), total_value=10000.0
            ),
            PortfolioSnapshot(
                datetime=datetime(2024, 1, 2, 12, 0), total_value=12000.0
            ),
            PortfolioSnapshot(
                datetime=datetime(2024, 1, 3, 12, 0), total_value=11000.0
            ),
        ]
        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = snapshots
        mock_session.query.return_value = mock_query

        result = storage.get_all_ordered()

        assert result == snapshots
        assert len(result) == 3
        mock_session.query.assert_called_once_with(PortfolioSnapshot)
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()

    def test_get_all_ordered_empty(self, mock_session):
        """Test getting all portfolio snapshots when none exist"""
        storage = PortfolioSnapshotStorage(mock_session)

        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query

        result = storage.get_all_ordered()

        assert result == []
        assert len(result) == 0

    def test_save_multiple_snapshots(self, mock_session):
        """Test saving multiple snapshots sequentially"""
        storage = PortfolioSnapshotStorage(mock_session)

        snapshot1 = PortfolioSnapshot(
            datetime=datetime(2024, 1, 1, 12, 0), total_value=10000.0
        )
        snapshot2 = PortfolioSnapshot(
            datetime=datetime(2024, 1, 2, 12, 0), total_value=12000.0
        )

        result1 = storage.save(snapshot1)
        result2 = storage.save(snapshot2)

        assert result1 is True
        assert result2 is True
        assert mock_session.add.call_count == 2
        assert mock_session.commit.call_count == 2
        mock_session.add.assert_any_call(snapshot1)
        mock_session.add.assert_any_call(snapshot2)

    def test_get_first_with_different_values(self, mock_session):
        """Test getting first snapshot with different values"""
        storage = PortfolioSnapshotStorage(mock_session)

        snapshot = PortfolioSnapshot(
            datetime=datetime(2024, 1, 5, 15, 30), total_value=50000.0
        )
        mock_query = Mock()
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = snapshot
        mock_session.query.return_value = mock_query

        result = storage.get_first()

        assert result.total_value == 50000.0
        assert result.datetime == datetime(2024, 1, 5, 15, 30)
