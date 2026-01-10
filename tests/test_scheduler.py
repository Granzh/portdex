import logging
from unittest.mock import ANY, MagicMock, Mock, patch

import pytest
from apscheduler.schedulers.blocking import BlockingScheduler

from scheduler.scheduler import start_scheduler


class TestScheduler:
    """Test cases for scheduler functionality"""

    @patch("scheduler.scheduler.BlockingScheduler")
    @patch("scheduler.scheduler.hourly_candle_update")
    @patch("scheduler.scheduler.portfolio_snapshot_job")
    @patch("scheduler.scheduler.portfolio_index_job")
    def test_start_scheduler_creates_jobs(
        self, mock_index_job, mock_snapshot_job, mock_candle_job, mock_scheduler_class
    ):
        """Test that start_scheduler creates all expected jobs"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.add_job.return_value = Mock(id="test_job")

        mock_services = {
            "backfill_service": Mock(),
            "snapshot_service": Mock(),
            "index_service": Mock(),
        }
        tickers = ["SBER", "GAZP"]

        start_scheduler(
            mock_services["backfill_service"],
            mock_services["snapshot_service"],
            mock_services["index_service"],
            tickers,
        )

        # Verify that scheduler was created
        mock_scheduler_class.assert_called_once()

        # Verify that 3 jobs were added
        assert mock_scheduler.add_job.call_count == 3

        # Verify scheduler.start was called
        mock_scheduler.start.assert_called_once()

    @patch("scheduler.scheduler.BlockingScheduler")
    def test_start_scheduler_candle_update_job(self, mock_scheduler_class):
        """Test candle update job configuration"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_job = Mock(id="hourly_candle_update")
        mock_scheduler.add_job.return_value = mock_job

        mock_backfill_service = Mock()
        mock_snapshot_service = Mock()
        mock_index_service = Mock()
        tickers = ["SBER"]

        start_scheduler(
            mock_backfill_service, mock_snapshot_service, mock_index_service, tickers
        )

        # Check first call (candle update job)
        mock_scheduler.add_job.assert_any_call(
            func=ANY,  # hourly_candle_update function
            trigger=ANY,  # CronTrigger
            kwargs={"backfill_service": mock_backfill_service, "tickers": tickers},
            id="hourly_candle_update",
            replace_existing=True,
            max_instances=1,
            coalesce=True,
        )

    @patch("scheduler.scheduler.BlockingScheduler")
    def test_start_scheduler_snapshot_job(self, mock_scheduler_class):
        """Test portfolio snapshot job configuration"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_job = Mock(id="portfolio_snapshot")
        mock_scheduler.add_job.return_value = mock_job

        mock_backfill_service = Mock()
        mock_snapshot_service = Mock()
        mock_index_service = Mock()
        tickers = ["SBER"]

        start_scheduler(
            mock_backfill_service, mock_snapshot_service, mock_index_service, tickers
        )

        # Check second call (snapshot job)
        calls = mock_scheduler.add_job.call_args_list
        snapshot_call = None
        for call in calls:
            if "portfolio_snapshot" in str(call):
                snapshot_call = call
                break

        assert snapshot_call is not None
        args, kwargs = snapshot_call
        assert kwargs["id"] == "portfolio_snapshot"
        assert "snapshot_service" in kwargs["kwargs"]

    @patch("scheduler.scheduler.BlockingScheduler")
    def test_start_scheduler_index_job(self, mock_scheduler_class):
        """Test portfolio index job configuration"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_job = Mock(id="portfolio_index")
        mock_scheduler.add_job.return_value = mock_job

        mock_backfill_service = Mock()
        mock_snapshot_service = Mock()
        mock_index_service = Mock()
        tickers = ["SBER"]

        start_scheduler(
            mock_backfill_service, mock_snapshot_service, mock_index_service, tickers
        )

        # Check third call (index job)
        calls = mock_scheduler.add_job.call_args_list
        index_call = None
        for call in calls:
            if "portfolio_index" in str(call):
                index_call = call
                break

        assert index_call is not None
        args, kwargs = index_call
        assert kwargs["id"] == "portfolio_index"
        assert "index_service" in kwargs["kwargs"]
        assert "snapshot_storage" in kwargs["kwargs"]

    @patch("scheduler.scheduler.BlockingScheduler")
    def test_start_scheduler_with_empty_tickers(self, mock_scheduler_class):
        """Test scheduler with empty tickers list"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_job = Mock(id="test_job")
        mock_scheduler.add_job.return_value = mock_job

        mock_services = {
            "backfill_service": Mock(),
            "snapshot_service": Mock(),
            "index_service": Mock(),
        }
        tickers = []

        start_scheduler(
            mock_services["backfill_service"],
            mock_services["snapshot_service"],
            mock_services["index_service"],
            tickers,
        )

        # Should still create 3 jobs even with empty tickers
        assert mock_scheduler.add_job.call_count == 3

    @patch("scheduler.scheduler.BlockingScheduler")
    def test_start_scheduler_job_configuration(self, mock_scheduler_class):
        """Test that all jobs have correct configuration"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_job = Mock(id="test_job")
        mock_scheduler.add_job.return_value = mock_job

        mock_services = {
            "backfill_service": Mock(),
            "snapshot_service": Mock(),
            "index_service": Mock(),
        }
        tickers = ["SBER", "GAZP"]

        start_scheduler(
            mock_services["backfill_service"],
            mock_services["snapshot_service"],
            mock_services["index_service"],
            tickers,
        )

        # Check that all calls have proper configuration
        for call in mock_scheduler.add_job.call_args_list:
            args, kwargs = call
            assert kwargs["replace_existing"] is True
            assert kwargs["max_instances"] == 1
            assert kwargs["coalesce"] is True
            assert "id" in kwargs
            assert "trigger" in kwargs
            assert "func" in kwargs
            assert "kwargs" in kwargs

    @patch("scheduler.scheduler.BlockingScheduler")
    def test_start_scheduler_logging(self, mock_scheduler_class, caplog):
        """Test that scheduler logs proper messages"""
        mock_scheduler = Mock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_job = Mock(id="test_job")
        mock_scheduler.add_job.return_value = mock_job
        mock_scheduler.get_job.return_value = Mock(next_run_time="2024-01-01 10:00:00")

        mock_backfill_service = Mock()
        mock_snapshot_service = Mock()
        mock_index_service = Mock()
        tickers = ["SBER"]

        with caplog.at_level(logging.INFO):
            start_scheduler(
                mock_backfill_service,
                mock_snapshot_service,
                mock_index_service,
                tickers,
            )
        # Check logged messages
        assert "Scheduler started" in caplog.text
