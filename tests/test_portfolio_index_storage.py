from datetime import datetime
from unittest.mock import Mock

import pytest

from db.models import PortfolioIndex
from storage.portfolio_index_storage import PortfolioIndexStorage


class TestPortfolioIndexStorage:
    """Test cases for PortfolioIndexStorage"""

    def test_init(self, mock_session):
        """Test PortfolioIndexStorage initialization"""
        storage = PortfolioIndexStorage(mock_session)
        assert storage.session == mock_session

    def test_save_success(self, mock_session):
        """Test successful save of portfolio index"""
        storage = PortfolioIndexStorage(mock_session)

        index = PortfolioIndex(datetime=datetime(2024, 1, 1, 12, 0), index_value=1000.0)

        result = storage.save(index)

        assert result is True
        mock_session.add.assert_called_once_with(index)
        mock_session.commit.assert_called_once()

    def test_save_other_exception_rollback(self, mock_session):
        """Test save failure with other exception and rollback"""
        storage = PortfolioIndexStorage(mock_session)

        index = PortfolioIndex(datetime=datetime(2024, 1, 1, 12, 0), index_value=1000.0)

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
            datetime=datetime(2024, 1, 1, 12, 0), index_value=1000.0
        )
        index2 = PortfolioIndex(
            datetime=datetime(2024, 1, 2, 12, 0), index_value=1050.0
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
                datetime=datetime(2024, 1, 1, 12, 0), index_value=index_value
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
            index = PortfolioIndex(datetime=test_datetime, index_value=1000.0)

            result = storage.save(index)

            assert result is True
            mock_session.add.assert_called_once_with(index)
            mock_session.commit.assert_called_once()

            # Check that correct datetime was passed
            added_index = mock_session.add.call_args[0][0]
            assert added_index.datetime == test_datetime
