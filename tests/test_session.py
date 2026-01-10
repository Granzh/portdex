from unittest.mock import Mock, patch

import pytest

from storage.session import SessionLocal, engine, init_db


class TestSessionModule:
    """Test cases for session module"""

    def test_engine_creation(self):
        """Test engine creation"""
        init_db()

        # Получаем engine после инициализации
        from storage.session import engine

        assert engine is not None
        assert hasattr(engine, "url")
        # SQLAlchemy 2.0+ использует connect, а не execute
        assert hasattr(engine, "connect")

    @patch("storage.session.Base")
    @patch("storage.session.create_engine")
    def test_init_db_calls_create_all(self, mock_create_engine, mock_base):
        """Test init_db calls create_all"""
        # Mock engine
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_base.metadata = Mock()

        # Вызываем init_db ПОСЛЕ применения патчей
        init_db()

        # Verify create_all was called with engine
        mock_base.metadata.create_all.assert_called_once_with(bind=mock_engine)

    def test_session_local_configuration(self):
        """Test SessionLocal configuration"""
        init_db()

        # Получаем SessionLocal после инициализации
        from storage.session import SessionLocal

        assert SessionLocal is not None
        assert callable(SessionLocal)

    @patch("storage.session.create_engine")
    def test_engine_parameters(self, mock_create_engine):
        """Test engine creation parameters"""
        mock_create_engine.return_value = Mock()

        init_db()

        # Verify create_engine was called with correct parameters
        mock_create_engine.assert_called_once_with(
            "sqlite:///./db/sqlite3", echo=False, future=True
        )

    @patch("storage.session.sessionmaker")
    @patch("storage.session.create_engine")
    def test_session_maker_configuration(self, mock_create_engine, mock_sessionmaker):
        """Test sessionmaker configuration"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker.return_value = Mock()

        init_db()

        # Verify sessionmaker was called with correct parameters
        mock_sessionmaker.assert_called_once_with(
            bind=mock_engine, autocommit=False, autoflush=False
        )

    def test_database_url(self):
        """Test database URL configuration"""
        init_db()

        from storage.session import engine

        # Check that correct database URL is used
        assert "sqlite:///./db/sqlite3" in str(engine.url)

    @patch("storage.session.sessionmaker")
    @patch("storage.session.create_engine")
    def test_module_level_objects(self, mock_create_engine, mock_sessionmaker):
        """Test that module-level objects are properly initialized"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker.return_value = Mock()

        init_db()

        # Verify both create_engine and sessionmaker were called
        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once()

    @patch("storage.session.create_engine")
    def test_engine_future_flag(self, mock_create_engine):
        """Test that engine is created with future=True"""
        mock_create_engine.return_value = Mock()

        init_db()

        # Check that future=True was passed
        call_kwargs = mock_create_engine.call_args.kwargs
        assert call_kwargs.get("future") is True

    @patch("storage.session.sessionmaker")
    @patch("storage.session.create_engine")
    def test_session_autocommit_false(self, mock_create_engine, mock_sessionmaker):
        """Test that SessionLocal has autocommit=False"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker.return_value = Mock()

        init_db()

        # Check that autocommit=False was passed
        call_kwargs = mock_sessionmaker.call_args.kwargs
        assert call_kwargs.get("autocommit") is False

    @patch("storage.session.create_engine")
    @patch("storage.session.sessionmaker")
    def test_session_autoflush_false(self, mock_sessionmaker, mock_create_engine):
        """Test that SessionLocal has autoflush=False"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker.return_value = Mock()

        init_db()

        # Check that autoflush=False was passed
        call_kwargs = mock_sessionmaker.call_args.kwargs
        assert call_kwargs.get("autoflush") is False

    @patch("storage.session.create_engine")
    def test_echo_false_flag(self, mock_create_engine):
        """Test that engine is created with echo=False"""
        mock_create_engine.return_value = Mock()

        init_db()

        # Check that echo=False was passed
        call_kwargs = mock_create_engine.call_args.kwargs
        assert call_kwargs.get("echo") is False
