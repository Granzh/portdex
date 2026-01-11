from datetime import datetime
from unittest.mock import Mock

import pytest

from db.models import PortfolioIndex
from storage.portfolio_index_storage import PortfolioIndexStorage


class TestPortfolioIndexStorage:
    """Test cases for PortfolioIndexStorage with focus on reset functionality"""

    def test_init(self, mock_session):
        """Test PortfolioIndexStorage initialization"""
        storage = PortfolioIndexStorage(mock_session)
        assert storage.session == mock_session

    def test_save_success(self, mock_session):
        """Test successful save of portfolio index"""
        storage = PortfolioIndexStorage(mock_session)

        index = PortfolioIndex(
            datetime=datetime(2024, 1, 1, 12, 0), index_value=1000.0, divisor=1.0
        )

        result = storage.save(index)

        assert result is True
        mock_session.add.assert_called_once_with(index)
        mock_session.commit.assert_called_once()

    def test_save_other_exception_rollback(self, mock_session):
        """Test save failure with other exception and rollback"""
        storage = PortfolioIndexStorage(mock_session)

        index = PortfolioIndex(
            datetime=datetime(2024, 1, 1, 12, 0), index_value=1000.0, divisor=1.0
        )

        # Mock commit to raise generic Exception
        mock_session.commit.side_effect = Exception("Database error")

        result = storage.save(index)

        assert result is False
        mock_session.add.assert_called_once_with(index)
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_called_once()

    def test_save_multiple_indices(self, mock_session):
        """Test saving multiple indices sequentially"""
        storage = PortfolioIndexStorage(mock_session)

        index1 = PortfolioIndex(
            datetime=datetime(2024, 1, 1, 12, 0), index_value=1000.0, divisor=1.0
        )
        index2 = PortfolioIndex(
            datetime=datetime(2024, 1, 2, 12, 0), index_value=1050.0, divisor=1.0
        )

        result1 = storage.save(index1)
        result2 = storage.save(index2)

        assert result1 is True
        assert result2 is True
        assert mock_session.add.call_count == 2
        assert mock_session.commit.call_count == 2
        mock_session.add.assert_any_call(index1)
        mock_session.add.assert_any_call(index2)

    def test_save_with_different_values(self, mock_session):
        """Test save with different index values"""
        storage = PortfolioIndexStorage(mock_session)

        test_cases = [
            (0.0, "Zero index value"),
            (-100.0, "Negative index value"),
            (1500.5, "Decimal index value"),
            (1000000.0, "Large index value"),
        ]

        for index_value, description in test_cases:
            mock_session.reset_mock()
            index = PortfolioIndex(
                datetime=datetime(2024, 1, 1, 12, 0),
                index_value=index_value,
                divisor=1.0,
            )

            result = storage.save(index)

            assert result is True
            mock_session.add.assert_called_once_with(index)
            mock_session.commit.assert_called_once()

    def test_save_with_different_datetimes(self, mock_session):
        """Test save with different datetime values"""
        storage = PortfolioIndexStorage(mock_session)

        test_cases = [
            datetime(2024, 1, 1, 0, 0, 0),
            datetime(2024, 1, 1, 23, 59, 59),
            datetime(2020, 1, 1, 12, 0, 0),  # Older date
            datetime(2030, 1, 1, 12, 0, 0),  # Future date
        ]

        for test_datetime in test_cases:
            mock_session.reset_mock()
            index = PortfolioIndex(
                datetime=test_datetime, index_value=1000.0, divisor=1.0
            )

            result = storage.save(index)

            assert result is True
            mock_session.add.assert_called_once_with(index)
            mock_session.commit.assert_called_once()

            # Check that correct datetime was passed
            added_index = mock_session.add.call_args[0][0]
            assert added_index.datetime == test_datetime

    def test_delete_all_success(self, mock_session):
        """Test successful deletion of all portfolio index data"""
        storage = PortfolioIndexStorage(mock_session)

        # Mock() query and delete methods
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.delete.return_value = 5  # Simulate 5 rows deleted

        storage.delete_all()

        # Verify query was called with PortfolioIndex model
        mock_session.query.assert_called_once_with(PortfolioIndex)

        # Verify delete was called
        mock_query.delete.assert_called_once()

        # Verify commit was called
        mock_session.commit.assert_called_once()

    def test_delete_all_empty_table(self, mock_session):
        """Test deletion when table is already empty"""
        storage = PortfolioIndexStorage(mock_session)

        # Mock() query and delete methods
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.delete.return_value = 0  # No rows deleted

        storage.delete_all()

        # Should still call delete and commit
        mock_query.delete.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_delete_all_with_exception(self, mock_session):
        """Test delete_all when database exception occurs"""
        storage = PortfolioIndexStorage(mock_session)

        # Mock() query and delete methods to raise exception
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.delete.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            storage.delete_all()

        # Verify delete was attempted
        mock_query.delete.assert_called_once()

        # Commit should not be called due to exception
        mock_session.commit.assert_not_called()

    def test_get_all_ordered_success(self, mock_session):
        """Test getting all portfolio indexes ordered by datetime"""
        storage = PortfolioIndexStorage(mock_session)

        # Mock() query results
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [
            PortfolioIndex(
                datetime=datetime(2024, 1, 1, 12, 0), index_value=1000.0, divisor=1.0
            ),
            PortfolioIndex(
                datetime=datetime(2024, 1, 2, 12, 0), index_value=1050.0, divisor=1.0
            ),
        ]

        result = storage.get_all_ordered()

        assert len(result) == 2
        mock_session.query.assert_called_once_with(PortfolioIndex)
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()

    def test_get_last_success(self, mock_session):
        """Test getting last portfolio index"""
        storage = PortfolioIndexStorage(mock_session)

        # Mock() query results
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = PortfolioIndex(
            datetime=datetime(2024, 1, 1, 12, 0), index_value=1000.0, divisor=1.0
        )

        result = storage.get_last()

        assert result is not None
        assert result.index_value == 1000.0
        mock_session.query.assert_called_once_with(PortfolioIndex)
        mock_query.order_by.assert_called_once()
        mock_query.first.assert_called_once()

    def test_get_last_not_found(self, mock_session):
        """Test getting last portfolio index when none exists"""
        storage = PortfolioIndexStorage(mock_session)

        # Mock() query results
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None

        result = storage.get_last()

        assert result is None
        mock_query.first.assert_called_once()

    def test_integration_save_and_delete(self, mock_session):
        """Test integration between save and delete_all operations"""
        storage = PortfolioIndexStorage(mock_session)

        # First save some data
        test_index = PortfolioIndex(
            datetime=datetime(2024, 1, 1, 12, 0), index_value=1000.0, divisor=1.0
        )

        storage.save(test_index)

        # Then delete all data
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.delete.return_value = 1

        storage.delete_all()

        # Verify both operations were called
        mock_session.add.assert_called_once_with(test_index)
        mock_session.commit.assert_called()  # Called twice (once for save, once for delete)
        mock_query.delete.assert_called_once()
