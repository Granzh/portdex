import pytest
from unittest.mock import Mock

from storage.security_storage import SecurityStorage
from db.models import Security


class TestSecurityStorage:
    """Test cases for SecurityStorage"""

    def test_init(self, mock_session):
        """Test SecurityStorage initialization"""
        storage = SecurityStorage(mock_session)
        assert storage.session == mock_session

    def test_get_or_create_existing_security(self, mock_session):
        """Test getting existing security"""
        storage = SecurityStorage(mock_session)

        existing_security = Security(
            ticker="SBER", board="TQBR", engine="stock", currency="RUB"
        )
        mock_session.get.return_value = existing_security

        result = storage.get_or_create(ticker="SBER")

        assert result == existing_security
        mock_session.get.assert_called_once_with(Security, "SBER")
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()

    def test_get_or_create_new_security_default_params(self, mock_session):
        """Test creating new security with default parameters"""
        storage = SecurityStorage(mock_session)

        mock_session.get.return_value = None  # Security doesn't exist

        result = storage.get_or_create(ticker="SBER")

        assert result.ticker == "SBER"
        assert result.board == "TQBR"
        assert result.engine == "stock"
        assert result.currency == "RUB"
        mock_session.get.assert_called_once_with(Security, "SBER")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_get_or_create_new_security_custom_params(self, mock_session):
        """Test creating new security with custom parameters"""
        storage = SecurityStorage(mock_session)

        mock_session.get.return_value = None  # Security doesn't exist

        result = storage.get_or_create(
            ticker="GAZP", board="TQBR", engine="stock", currency="RUB"
        )

        assert result.ticker == "GAZP"
        assert result.board == "TQBR"
        assert result.engine == "stock"
        assert result.currency == "RUB"
        mock_session.get.assert_called_once_with(Security, "GAZP")
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_get_or_create_new_security_different_board(self, mock_session):
        """Test creating new security with different board"""
        storage = SecurityStorage(mock_session)

        mock_session.get.return_value = None

        result = storage.get_or_create(
            ticker="SBER", board="MAIN", engine="stock", currency="RUB"
        )

        assert result.board == "MAIN"
        mock_session.add.assert_called_once()

        # Check the added security
        added_security = mock_session.add.call_args[0][0]
        assert added_security.board == "MAIN"

    def test_get_or_create_new_security_different_engine(self, mock_session):
        """Test creating new security with different engine"""
        storage = SecurityStorage(mock_session)

        mock_session.get.return_value = None

        result = storage.get_or_create(ticker="SBER", engine="bond", currency="USD")

        assert result.engine == "bond"
        assert result.currency == "USD"

    def test_get_or_create_multiple_calls(self, mock_session):
        """Test multiple get_or_create calls"""
        storage = SecurityStorage(mock_session)

        # First call - create new
        mock_session.get.return_value = None
        result1 = storage.get_or_create(ticker="SBER")
        assert result1.ticker == "SBER"

        # Second call - existing security
        existing_security = Security(
            ticker="GAZP", board="TQBR", engine="stock", currency="RUB"
        )
        mock_session.get.return_value = existing_security
        result2 = storage.get_or_create(ticker="GAZP")
        assert result2 == existing_security

        assert mock_session.get.call_count == 2
        assert mock_session.add.call_count == 1  # Only added once for SBER
        assert mock_session.commit.call_count == 1

    def test_get_or_create_edge_cases(self, mock_session):
        """Test edge cases for get_or_create"""
        storage = SecurityStorage(mock_session)

        # Test with empty ticker
        mock_session.get.return_value = None
        result = storage.get_or_create(ticker="")
        assert result.ticker == ""

        # Test with special characters in ticker
        mock_session.reset_mock()
        mock_session.get.return_value = None
        result = storage.get_or_create(ticker="BR.A")
        assert result.ticker == "BR.A"

    def test_get_or_create_session_interaction(self, mock_session):
        """Test detailed session interaction"""
        storage = SecurityStorage(mock_session)

        # Mock session methods to track exact calls
        mock_session.get.return_value = None

        result = storage.get_or_create(
            ticker="TEST",
            board="TEST_BOARD",
            engine="TEST_ENGINE",
            currency="TEST_CURR",
        )

        # Verify get was called with correct parameters
        mock_session.get.assert_called_once_with(Security, "TEST")

        # Verify add was called with correct Security object
        added_security = mock_session.add.call_args[0][0]
        assert added_security.ticker == "TEST"
        assert added_security.board == "TEST_BOARD"
        assert added_security.engine == "TEST_ENGINE"
        assert added_security.currency == "TEST_CURR"

        # Verify commit was called
        mock_session.commit.assert_called_once()

    def test_get_or_create_preserves_existing(self, mock_session):
        """Test that existing security is not modified"""
        storage = SecurityStorage(mock_session)

        existing_security = Security(
            ticker="SBER", board="OLD_BOARD", engine="stock", currency="RUB"
        )
        mock_session.get.return_value = existing_security

        result = storage.get_or_create(
            ticker="SBER",
            board="NEW_BOARD",  # Different board
            engine="bond",  # Different engine
            currency="USD",  # Different currency
        )

        # Should return existing security unchanged
        assert result == existing_security
        assert result.board == "OLD_BOARD"
        assert result.engine == "stock"
        assert result.currency == "RUB"

        # Should not call add or commit
        mock_session.add.assert_not_called()
        mock_session.commit.assert_not_called()
