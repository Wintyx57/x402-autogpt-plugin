"""
Unit tests for examples/standalone_usage.py

Tests the main() function with mocked X402Client, covering:
- Connection failure early return
- Happy path (all calls succeed)
- Payment-required flow
- Exception handling in each section
- Convenience methods (crypto, search, image, scraper)
"""

import io
import sys
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# Add examples directory to path so we can import standalone_usage
sys.path.insert(0, str(Path(__file__).parent.parent / "examples"))
# Add src to path for x402_bazaar imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import standalone_usage
from standalone_usage import main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _capture_main(**client_attrs):
    """Run main() with a mocked X402Client and return stdout as a string."""
    mock_client = MagicMock()
    for attr, val in client_attrs.items():
        setattr(mock_client, attr, val)

    buf = io.StringIO()
    with patch("standalone_usage.X402Client", return_value=mock_client):
        with redirect_stdout(buf):
            main()

    return buf.getvalue(), mock_client


def _make_services(n=3):
    """Return n fake service dicts."""
    return [
        {
            "name": f"Service {i}",
            "description": f"Description {i}",
            "endpoint": f"/api/service{i}",
            "cost_usdc": f"0.{i:02d}",
            "category": "test",
            "tags": [],
        }
        for i in range(1, n + 1)
    ]


def _make_weather_services():
    return [
        {
            "name": "Weather API",
            "description": "Real-time weather data",
            "endpoint": "/api/weather",
            "cost_usdc": "0.01",
            "category": "weather",
            "tags": ["weather"],
        }
    ]


def _payment_required_result(cost="0.01"):
    return {
        "success": False,
        "payment_required": True,
        "cost_usdc": cost,
        "payment_details": {
            "payment_amount": cost,
            "payment_address": "0xfb1c478BD5567BdcD39782E0D6D23418bFda2430",
            "payment_chain": "base",
            "payment_token": "USDC",
            "message": f"Payment required: {cost} USDC",
            "instructions": [
                f"1. Send {cost} USDC on BASE to: 0xfb1c478BD5567BdcD39782E0D6D23418bFda2430",
                "2. Wait for transaction confirmation",
                "3. Call this endpoint again with transaction hash",
            ],
        },
    }


def _success_result(data):
    return {"success": True, "data": data, "payment_status": "free"}


def _error_result(msg="Some error"):
    return {"success": False, "error": msg}


# ---------------------------------------------------------------------------
# Test: connection failure
# ---------------------------------------------------------------------------

class TestMainConnectionFailure:
    def test_exits_early_when_not_connected(self):
        buf = io.StringIO()
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = False

        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()

        output = buf.getvalue()
        assert "Connection: FAILED" in output
        assert "Cannot connect to marketplace" in output
        # No further sections should run
        assert "marketplace statistics" not in output.lower()

    def test_no_api_calls_after_connection_failure(self):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = False

        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(io.StringIO()):
                main()

        mock_client.get_public_stats.assert_not_called()
        mock_client.discover_services.assert_not_called()
        mock_client.search_services.assert_not_called()


# ---------------------------------------------------------------------------
# Test: header / footer output
# ---------------------------------------------------------------------------

class TestMainOutputStructure:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_client = MagicMock()
        self.mock_client.base_url = "https://x402-api.onrender.com"
        self.mock_client.test_connection.return_value = True
        self.mock_client.get_public_stats.return_value = {}
        self.mock_client.discover_services.return_value = []
        self.mock_client.search_services.return_value = []
        self.mock_client.call_api.return_value = _error_result("not found")
        self.mock_client.call_weather_api.return_value = _error_result()
        self.mock_client.get_service_details.return_value = None
        self.mock_client.call_crypto_api.return_value = _error_result()
        self.mock_client.call_search_api.return_value = _error_result()
        self.mock_client.call_image_api.return_value = _error_result()
        self.mock_client.call_scraper_api.return_value = _error_result()

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=self.mock_client):
            with redirect_stdout(buf):
                main()
        self.output = buf.getvalue()

    def test_banner_present(self):
        assert "x402 Bazaar Client - Standalone Example" in self.output

    def test_client_url_shown(self):
        assert "https://x402-api.onrender.com" in self.output

    def test_connection_ok_shown(self):
        assert "Connection: OK" in self.output

    def test_example_complete_shown(self):
        assert "Example Complete" in self.output

    def test_next_steps_shown(self):
        assert "Next steps" in self.output

    def test_all_section_numbers_present(self):
        for i in range(1, 9):
            assert f"{i}." in self.output


# ---------------------------------------------------------------------------
# Test: section 2 — marketplace stats
# ---------------------------------------------------------------------------

class TestSection2Stats:
    def _run(self, stats_return=None, stats_raises=None):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        if stats_raises:
            mock_client.get_public_stats.side_effect = stats_raises
        else:
            mock_client.get_public_stats.return_value = stats_return or {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()
        return buf.getvalue()

    def test_stats_displayed(self):
        stats = {
            "services": {"total": 42},
            "apiCalls": {"total": 1000},
            "integrations": {"total": 7},
        }
        output = self._run(stats_return=stats)
        assert "42" in output
        assert "1000" in output
        assert "7" in output

    def test_stats_missing_fields_shows_na(self):
        output = self._run(stats_return={})
        assert "N/A" in output

    def test_stats_exception_handled(self):
        output = self._run(stats_raises=Exception("network error"))
        assert "Error" in output
        assert "network error" in output
        # Should continue to next sections
        assert "Discovering all services" in output


# ---------------------------------------------------------------------------
# Test: section 3 — discover services
# ---------------------------------------------------------------------------

class TestSection3Discover:
    def _run(self, services=None, raises=None):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        if raises:
            mock_client.discover_services.side_effect = raises
        else:
            mock_client.discover_services.return_value = services if services is not None else []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()
        return buf.getvalue()

    def test_service_count_displayed(self):
        output = self._run(services=_make_services(5))
        assert "Found 5 APIs" in output

    def test_zero_services_displayed(self):
        output = self._run(services=[])
        assert "Found 0 APIs" in output

    def test_first_five_services_shown(self):
        services = _make_services(7)
        output = self._run(services=services)
        # Only first 5 should be listed
        assert "Service 1" in output
        assert "Service 5" in output
        assert "Service 6" not in output
        assert "Service 7" not in output

    def test_fewer_than_five_services_shown(self):
        services = _make_services(3)
        output = self._run(services=services)
        assert "Service 1" in output
        assert "Service 3" in output

    def test_service_cost_displayed(self):
        output = self._run(services=_make_services(2))
        assert "USDC" in output

    def test_exception_handled(self):
        output = self._run(raises=Exception("timeout"))
        assert "Error" in output
        assert "timeout" in output
        # Should still show section 4
        assert "Searching for" in output


# ---------------------------------------------------------------------------
# Test: section 4 — search services
# ---------------------------------------------------------------------------

class TestSection4Search:
    def _run(self, search_results=None, raises=None):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        if raises:
            mock_client.search_services.side_effect = raises
        else:
            mock_client.search_services.return_value = search_results if search_results is not None else []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()
        return buf.getvalue()

    def test_search_query_shown(self):
        output = self._run()
        assert "weather" in output.lower()

    def test_results_count_shown(self):
        output = self._run(search_results=_make_weather_services())
        assert "Found 1 weather-related APIs" in output

    def test_service_fields_displayed(self):
        output = self._run(search_results=_make_weather_services())
        assert "Weather API" in output
        assert "Real-time weather data" in output
        assert "/api/weather" in output

    def test_zero_results(self):
        output = self._run(search_results=[])
        assert "Found 0 weather-related APIs" in output

    def test_exception_handled(self):
        output = self._run(raises=RuntimeError("search failed"))
        assert "Error" in output
        assert "search failed" in output
        assert "free endpoint" in output.lower()

    def test_search_called_with_weather(self):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(io.StringIO()):
                main()

        mock_client.search_services.assert_called_once_with("weather")


# ---------------------------------------------------------------------------
# Test: section 5 — call free API
# ---------------------------------------------------------------------------

class TestSection5FreeAPI:
    def _run(self, call_api_return=None, raises=None):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        if raises:
            mock_client.call_api.side_effect = raises
        else:
            mock_client.call_api.return_value = call_api_return or _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()
        return buf.getvalue()

    def test_success_shows_service_count(self):
        services = _make_services(10)
        output = self._run(call_api_return=_success_result(services))
        assert "Received 10 services" in output

    def test_error_shown(self):
        output = self._run(call_api_return=_error_result("endpoint not found"))
        assert "endpoint not found" in output

    def test_exception_handled(self):
        output = self._run(raises=ConnectionError("refused"))
        assert "Error" in output
        assert "refused" in output

    def test_called_with_services_endpoint(self):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(io.StringIO()):
                main()

        mock_client.call_api.assert_called_once_with("/api/services")


# ---------------------------------------------------------------------------
# Test: section 6 — weather API (paid)
# ---------------------------------------------------------------------------

class TestSection6WeatherAPI:
    def _run(self, weather_return=None, raises=None):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        if raises:
            mock_client.call_weather_api.side_effect = raises
        else:
            mock_client.call_weather_api.return_value = weather_return or _error_result()
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()
        return buf.getvalue()

    def test_payment_required_shows_details(self):
        output = self._run(weather_return=_payment_required_result("0.05"))
        assert "Payment Required" in output
        assert "0.05" in output
        assert "0xfb1c478BD5567BdcD39782E0D6D23418bFda2430" in output
        assert "BASE" in output

    def test_payment_required_shows_instructions(self):
        result = _payment_required_result("0.05")
        output = self._run(weather_return=result)
        assert "Instructions" in output
        assert "transaction hash" in output.lower()

    def test_success_shows_weather_data(self):
        weather_data = {"temperature": 22, "conditions": "Sunny"}
        output = self._run(
            weather_return=_success_result(weather_data)
        )
        assert "22" in output
        assert "Sunny" in output

    def test_error_shown(self):
        output = self._run(weather_return=_error_result("invalid city"))
        assert "invalid city" in output

    def test_exception_handled(self):
        output = self._run(raises=ValueError("bad input"))
        assert "Error" in output
        assert "bad input" in output
        # Section 7 should still run
        assert "details for" in output.lower()

    def test_called_with_paris(self):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(io.StringIO()):
                main()

        mock_client.call_weather_api.assert_called_once_with("Paris")


# ---------------------------------------------------------------------------
# Test: section 7 — get service details
# ---------------------------------------------------------------------------

class TestSection7ServiceDetails:
    def _run(self, details_return=None, raises=None):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        if raises:
            mock_client.get_service_details.side_effect = raises
        else:
            mock_client.get_service_details.return_value = details_return
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()
        return buf.getvalue()

    def test_service_found_shows_fields(self):
        details = {
            "name": "Weather API",
            "description": "Real-time weather",
            "endpoint": "/api/weather",
            "cost_usdc": "0.01",
            "category": "weather",
        }
        output = self._run(details_return=details)
        assert "Weather API" in output
        assert "Real-time weather" in output
        assert "/api/weather" in output
        assert "0.01" in output
        assert "weather" in output

    def test_service_not_found(self):
        output = self._run(details_return=None)
        assert "Service not found" in output

    def test_exception_handled(self):
        output = self._run(raises=Exception("db error"))
        assert "Error" in output
        assert "db error" in output
        # Section 8 should still run
        assert "convenience methods" in output.lower()

    def test_called_with_weather_api(self):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(io.StringIO()):
                main()

        mock_client.get_service_details.assert_called_once_with("Weather API")


# ---------------------------------------------------------------------------
# Test: section 8 — convenience methods
# ---------------------------------------------------------------------------

class TestSection8ConvenienceMethods:
    def _make_client(self, crypto=None, search=None, image=None, scraper=None,
                     crypto_raises=None, search_raises=None,
                     image_raises=None, scraper_raises=None):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _error_result()
        mock_client.get_service_details.return_value = None

        if crypto_raises:
            mock_client.call_crypto_api.side_effect = crypto_raises
        else:
            mock_client.call_crypto_api.return_value = crypto or _error_result()

        if search_raises:
            mock_client.call_search_api.side_effect = search_raises
        else:
            mock_client.call_search_api.return_value = search or _error_result()

        if image_raises:
            mock_client.call_image_api.side_effect = image_raises
        else:
            mock_client.call_image_api.return_value = image or _error_result()

        if scraper_raises:
            mock_client.call_scraper_api.side_effect = scraper_raises
        else:
            mock_client.call_scraper_api.return_value = scraper or _error_result()

        return mock_client

    def _run(self, **kwargs):
        mock_client = self._make_client(**kwargs)
        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()
        return buf.getvalue(), mock_client

    def test_crypto_payment_required_shows_cost(self):
        output, _ = self._run(crypto=_payment_required_result("0.02"))
        assert "Payment required" in output
        assert "0.02" in output

    def test_crypto_success_shown(self):
        output, _ = self._run(crypto=_success_result({"price": 50000}))
        assert "Success! Data received" in output

    def test_crypto_exception_handled(self):
        output, _ = self._run(crypto_raises=Exception("timeout"))
        assert "Error" in output
        assert "timeout" in output

    def test_search_payment_required_shown(self):
        output, _ = self._run(search=_payment_required_result("0.01"))
        assert "Payment required" in output

    def test_search_success_shown(self):
        output, _ = self._run(search=_success_result([{"title": "Bitcoin news"}]))
        assert "Success! Data received" in output

    def test_search_exception_handled(self):
        output, _ = self._run(search_raises=RuntimeError("search error"))
        assert "Error" in output
        assert "search error" in output

    def test_image_payment_required_shown(self):
        output, _ = self._run(image=_payment_required_result("0.10"))
        assert "Payment required" in output
        assert "0.10" in output

    def test_image_success_shown(self):
        output, _ = self._run(image=_success_result({"url": "http://img.example.com/1.png"}))
        assert "Success! Data received" in output

    def test_image_exception_handled(self):
        output, _ = self._run(image_raises=IOError("image error"))
        assert "Error" in output

    def test_scraper_payment_required_shown(self):
        output, _ = self._run(scraper=_payment_required_result("0.03"))
        assert "Payment required" in output

    def test_scraper_success_shown(self):
        output, _ = self._run(scraper=_success_result({"html": "<html>"}))
        assert "Success! Data received" in output

    def test_scraper_exception_handled(self):
        output, _ = self._run(scraper_raises=Exception("scrape failed"))
        assert "Error" in output
        assert "scrape failed" in output

    def test_all_four_methods_called(self):
        _, mock_client = self._run()
        mock_client.call_crypto_api.assert_called_once_with("BTC")
        mock_client.call_search_api.assert_called_once_with("bitcoin")
        mock_client.call_image_api.assert_called_once_with("a beautiful sunset")
        mock_client.call_scraper_api.assert_called_once_with("https://example.com")


# ---------------------------------------------------------------------------
# Test: X402Client instantiation (module-level)
# ---------------------------------------------------------------------------

class TestClientInstantiation:
    def test_client_created_with_no_args(self):
        """main() should instantiate X402Client() without arguments."""
        captured_args = []
        captured_kwargs = []

        class FakeClient:
            base_url = "https://x402-api.onrender.com"

            def __init__(self, *args, **kwargs):
                captured_args.extend(args)
                captured_kwargs.extend(kwargs.keys())
                self.test_connection = MagicMock(return_value=False)

        with patch("standalone_usage.X402Client", FakeClient):
            with redirect_stdout(io.StringIO()):
                main()

        assert captured_args == []
        assert captured_kwargs == []

    def test_base_url_printed_after_init(self):
        mock_client = MagicMock()
        mock_client.base_url = "https://custom.example.com"
        mock_client.test_connection.return_value = False

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()

        assert "https://custom.example.com" in buf.getvalue()


# ---------------------------------------------------------------------------
# Test: payment details sub-structure in section 6
# ---------------------------------------------------------------------------

class TestPaymentDetailsOutput:
    def test_all_payment_fields_shown(self):
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _payment_required_result("0.05")
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()

        output = buf.getvalue()
        assert "Amount:" in output
        assert "Address:" in output
        assert "Chain:" in output
        assert "Instructions:" in output
        # Payment flow instructions
        assert "transaction hash" in output.lower()

    def test_payment_na_temperature_not_shown(self):
        """When payment_required, temperature/conditions should not appear."""
        mock_client = MagicMock()
        mock_client.base_url = "https://x402-api.onrender.com"
        mock_client.test_connection.return_value = True
        mock_client.get_public_stats.return_value = {}
        mock_client.discover_services.return_value = []
        mock_client.search_services.return_value = []
        mock_client.call_api.return_value = _error_result()
        mock_client.call_weather_api.return_value = _payment_required_result("0.01")
        mock_client.get_service_details.return_value = None
        mock_client.call_crypto_api.return_value = _error_result()
        mock_client.call_search_api.return_value = _error_result()
        mock_client.call_image_api.return_value = _error_result()
        mock_client.call_scraper_api.return_value = _error_result()

        buf = io.StringIO()
        with patch("standalone_usage.X402Client", return_value=mock_client):
            with redirect_stdout(buf):
                main()

        output = buf.getvalue()
        assert "Temperature:" not in output
        assert "Conditions:" not in output
