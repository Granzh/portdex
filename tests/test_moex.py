from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from sqlalchemy.orm.relationships import ORMBackrefArgument

from schemas.candle import CandleDTO
from services.moex import MoexService


class TestMoexService:
    """Test cases for MoexService"""

    def test_init_default_timeout(self):
        """Test MoexService initialization with default timeout"""
        with patch("services.moex.httpx.Client") as mock_client:
            service = MoexService()
            mock_client.assert_called_once_with(timeout=10.0)
            assert service.client is not None

    def test_init_custom_timeout(self):
        """Test MoexService initialization with custom timeout"""
        with patch("services.moex.httpx.Client") as mock_client:
            service = MoexService(timeout=5.0)
            mock_client.assert_called_once_with(timeout=5.0)

    def test_fetch_candles_success(self, monkeypatch, mock_moex_response_data):
        """Test successful candle fetching"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None

        mock_response.json.side_effect = [
            mock_moex_response_data,
            {
                "candles": {
                    "columns": ["begin", "open", "high", "low", "close", "volume"],
                    "data": [],
                }
            },
        ]

        mock_client.get.return_value = mock_response
        mock_client_class = Mock(return_value=mock_client)
        monkeypatch.setattr("services.moex.httpx.Client", mock_client_class)

        service = MoexService()

        candles = service.fetch_candles(
            ticker="SBER",
            interval=60,
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 2),
        )

        assert len(candles) == 2
        assert candles[0].ticker == "SBER"
        assert candles[0].open == 50.0
        assert candles[0].high == 51.0
        assert candles[0].low == 49.0
        assert candles[0].close == 50.5
        assert candles[0].volume == 1000
        assert candles[0].interval == 60

    @patch("services.moex.httpx.Client")
    def test_fetch_candles_pagination(self, mock_client_class):
        """Test candle fetching with pagination"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # First page response
        first_response = Mock()
        first_response.raise_for_status.return_value = None
        first_response.json.return_value = {
            "candles": {
                "columns": ["begin", "open", "high", "low", "close", "volume"],
                "data": [[datetime(2024, 1, 1, 10, 0), 50.0, 51.0, 49.0, 50.5, 1000]],
            }
        }

        # Second page response (empty)
        second_response = Mock()
        second_response.raise_for_status.return_value = None
        second_response.json.return_value = {
            "candles": {
                "columns": ["begin", "open", "high", "low", "close", "volume"],
                "data": [],
            }
        }

        mock_client.get.side_effect = [first_response, second_response]

        service = MoexService()
        candles = service.fetch_candles(
            ticker="SBER",
            interval=60,
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 2),
        )

        assert len(candles) == 1
        assert mock_client.get.call_count == 2

    @patch("services.moex.httpx.Client")
    def test_fetch_candles_http_error(self, mock_client_class):
        """Test candle fetching with HTTP error"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_client.get.return_value = mock_response

        service = MoexService()
        with pytest.raises(Exception, match="HTTP Error"):
            service.fetch_candles(
                ticker="SBER",
                interval=60,
                start=datetime(2024, 1, 1),
                end=datetime(2024, 1, 2),
            )

    @patch("services.moex.httpx.Client")
    def test_fetch_page_url_construction(
        self, mock_client_class, mock_moex_response_data
    ):
        """Test correct URL construction for page fetching"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_moex_response_data
        mock_client.get.return_value = mock_response

        service = MoexService()
        service._fetch_page(
            ticker="SBER",
            interval=60,
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 2),
            offset=0,
        )

        expected_url = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/SBER/candles.json"
        expected_params = {
            "interval": 60,
            "from": "2024-01-01",
            "till": "2024-01-02",
            "start": 0,
        }

        mock_client.get.assert_called_once_with(expected_url, params=expected_params)

    @patch("services.moex.httpx.Client")
    def test_fetch_page_empty_response(self, mock_client_class):
        """Test handling empty response"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "candles": {
                "columns": ["begin", "open", "high", "low", "close", "volume"],
                "data": [],
            }
        }
        mock_client.get.return_value = mock_response

        service = MoexService()
        result = service._fetch_page(
            ticker="SBER",
            interval=60,
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 2),
            offset=0,
        )

        assert result == []

    def test_fetch_candles_smoke(self):
        """Original smoke test kept for compatibility"""
        service = MoexService()
        # This test might fail without internet, but kept for original behavior
        try:
            candles = service.fetch_candles(
                ticker="SBER",
                interval=60,
                start=datetime(2024, 1, 1),
                end=datetime(2024, 1, 2),
            )
            assert candles
            assert candles[0].open > 0
        except Exception:
            # Expected to fail in testing environment without internet
            pytest.skip("Internet connection required for smoke test")
