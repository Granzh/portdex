from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from db.models import PortfolioIndex
from storage.index_storage import IndexStorage


class TestIndexStorage:
    """Test cases for IndexStorage"""

    def test_init(self, mock_session):
        """Test IndexStorage initialization"""
        storage = IndexStorage(mock_session)
        assert storage.session == mock_session

    def test_save_point_success(self, mock_session):
        """Test successful save of portfolio index point"""
        storage = IndexStorage(mock_session)

        test_datetime = datetime(2024, 1, 1, 12, 0)
        test_value = 1000.5
        test_divisor = 1.0

        storage.save_point(test_datetime, test_value, test_divisor)

        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()

        # Check that merge was called with correct PortfolioIndex
        merge_call_args = mock_session.merge.call_args[0][0]
        assert merge_call_args.datetime == test_datetime
        assert merge_call_args.index_value == test_value
        assert merge_call_args.divisor == test_divisor

    def test_save_point_multiple_calls(self, mock_session):
        """Test multiple save_point calls"""
        storage = IndexStorage(mock_session)

        points = [
            (datetime(2024, 1, 1, 12, 0), 1000.0, 1.0),
            (datetime(2024, 1, 2, 12, 0), 1050.5, 1.1),
            (datetime(2024, 1, 3, 12, 0), 1025.25, 1.2),
        ]

        for dt, value, divisor in points:
            storage.save_point(dt, value, divisor)

        assert mock_session.merge.call_count == 3
        assert mock_session.commit.call_count == 3

    def test_save_point_with_zero_value(self, mock_session):
        """Test save_point with zero value"""
        storage = IndexStorage(mock_session)

        test_datetime = datetime(2024, 1, 1, 12, 0)
        test_divisor = 1.0

        storage.save_point(test_datetime, 0.0, test_divisor)

        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()

        merge_call_args = mock_session.merge.call_args[0][0]
        assert merge_call_args.index_value == 0.0

    def test_save_point_with_negative_value(self, mock_session):
        """Test save_point with negative value"""
        storage = IndexStorage(mock_session)

        test_datetime = datetime(2024, 1, 1, 12, 0)
        test_divisor = 1.0

        storage.save_point(test_datetime, -100.0, test_divisor)

        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()

        merge_call_args = mock_session.merge.call_args[0][0]
        assert merge_call_args.index_value == -100.0

    def test_save_point_with_decimal_value(self, mock_session):
        """Test save_point with decimal value"""
        storage = IndexStorage(mock_session)

        test_datetime = datetime(2024, 1, 1, 12, 0)
        test_divisor = 1.0

        storage.save_point(test_datetime, 1234.56789, test_divisor)

        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()

        merge_call_args = mock_session.merge.call_args[0][0]
        assert merge_call_args.index_value == 1234.56789

    def test_save_point_with_different_datetimes(self, mock_session):
        """Test save_point with different datetime formats"""
        test_cases = [
            datetime(2024, 1, 1, 0, 0, 0),  # Midnight
            datetime(2024, 1, 1, 23, 59, 59),  # End of day
            datetime(2020, 1, 1, 12, 0, 0),  # Past date
            datetime(2030, 1, 1, 12, 0, 0),  # Future date
        ]

        for test_datetime in test_cases:
            mock_session = Mock()
            storage = IndexStorage(mock_session)

            storage.save_point(test_datetime, 1000.0, 1.0)

            merge_call_args = mock_session.merge.call_args[0][0]
            mock_session.merge.assert_called_once()
            assert merge_call_args.datetime == test_datetime

    def test_save_point_with_large_value(self, mock_session):
        """Test save_point with very large value"""
        storage = IndexStorage(mock_session)

        test_datetime = datetime(2024, 1, 1, 12, 0)
        large_value = 999999999.99
        test_divisor = 1.0

        storage.save_point(test_datetime, large_value, test_divisor)

        mock_session.merge.assert_called_once()
        mock_session.commit.assert_called_once()

        merge_call_args = mock_session.merge.call_args[0][0]
        assert merge_call_args.index_value == large_value

    def test_save_point_merge_interaction(self, mock_session):
        """Test detailed merge interaction"""
        storage = IndexStorage(mock_session)

        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        test_value = 1000.0
        test_divisor = 1.0

        storage.save_point(test_datetime, test_value, test_divisor)

        # Verify merge was called with PortfolioIndex instance
        merge_call = mock_session.merge.call_args
        assert merge_call is not None

        portfolio_index = merge_call[0][0]
        assert hasattr(portfolio_index, "datetime")
        assert hasattr(portfolio_index, "index_value")
        assert hasattr(portfolio_index, "divisor")

    def test_save_point_type_assertion(self, mock_session):
        """Test that saved object has correct attributes"""
        storage = IndexStorage(mock_session)

        test_datetime = datetime(2024, 1, 1, 12, 0)
        test_value = 1000.0
        test_divisor = 1.0

        storage.save_point(test_datetime, test_value, test_divisor)

        # Get the merged object
        merged_object = mock_session.merge.call_args[0][0]

        # Verify it's a PortfolioIndex instance
        assert type(merged_object).__name__ == "PortfolioIndex"

        # Verify attributes exist and are correct type
        assert hasattr(merged_object, "datetime")
        assert hasattr(merged_object, "index_value")
        assert hasattr(merged_object, "divisor")
        assert isinstance(merged_object.datetime, datetime)
        assert isinstance(merged_object.index_value, float)
        assert isinstance(merged_object.divisor, float)
