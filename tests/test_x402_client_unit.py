"""
Unit tests for X402Client — full mock coverage (no network calls).

Covers all branches of x402_client.py:
- __init__, discover_services, search_services, get_marketplace_info
- call_api (GET/POST, 200/402/400/429/500/other, timeout, RequestException, bad method)
- get_service_details, test_connection, get_public_stats
- convenience methods (weather, search, crypto, image, scraper)
"""

import json
import pytest
import requests
from unittest.mock import MagicMock, patch, call
from x402_bazaar.x402_client import X402Client


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(status_code=200, json_data=None, text="", raise_for_status=None):
    """Build a mock requests.Response."""
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text

    if json_data is not None:
        resp.json.return_value = json_data
    else:
        resp.json.side_effect = json.JSONDecodeError("no json", "", 0)

    if raise_for_status:
        resp.raise_for_status.side_effect = raise_for_status
    else:
        resp.raise_for_status.return_value = None

    return resp


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------

class TestX402ClientInit:
    def test_default_values(self):
        c = X402Client()
        assert c.base_url == "https://x402-api.onrender.com"
        assert c.timeout == 30
        assert c.PAYMENT_ADDRESS == "0xfb1c478BD5567BdcD39782E0D6D23418bFda2430"
        assert c.PAYMENT_CHAIN == "base"

    def test_custom_base_url(self):
        c = X402Client(base_url="http://localhost:9999")
        assert c.base_url == "http://localhost:9999"

    def test_custom_timeout(self):
        c = X402Client(timeout=5)
        assert c.timeout == 5

    def test_session_headers_set(self):
        c = X402Client()
        assert "x402-autogpt-plugin" in c.session.headers["User-Agent"]
        assert c.session.headers["Accept"] == "application/json"

    def test_session_created(self):
        c = X402Client()
        assert c.session is not None


# ---------------------------------------------------------------------------
# discover_services
# ---------------------------------------------------------------------------

class TestDiscoverServices:
    @pytest.fixture
    def client(self):
        return X402Client()

    def test_success_returns_list(self, client):
        services = [{"name": "Weather API", "description": "weather", "endpoint": "/api/weather"}]
        resp = _mock_response(200, json_data=services)
        client.session.get = MagicMock(return_value=resp)

        result = client.discover_services()
        assert result == services
        client.session.get.assert_called_once_with(
            "https://x402-api.onrender.com/api/services", timeout=30
        )

    def test_raises_on_request_exception(self, client):
        client.session.get = MagicMock(side_effect=requests.RequestException("timeout"))
        with pytest.raises(requests.RequestException):
            client.discover_services()

    def test_raises_on_http_error(self, client):
        resp = _mock_response(500, raise_for_status=requests.HTTPError("500"))
        client.session.get = MagicMock(return_value=resp)
        with pytest.raises(requests.HTTPError):
            client.discover_services()

    def test_uses_custom_base_url(self):
        client = X402Client(base_url="http://localhost:1234")
        services = [{"name": "X"}]
        resp = _mock_response(200, json_data=services)
        client.session.get = MagicMock(return_value=resp)

        client.discover_services()
        client.session.get.assert_called_once_with(
            "http://localhost:1234/api/services", timeout=30
        )


# ---------------------------------------------------------------------------
# search_services
# ---------------------------------------------------------------------------

class TestSearchServices:
    @pytest.fixture
    def client(self):
        return X402Client()

    def _patch_discover(self, client, services):
        client.discover_services = MagicMock(return_value=services)

    def test_matches_by_name(self, client):
        self._patch_discover(client, [
            {"name": "Weather API", "description": "clouds", "tags": []},
            {"name": "Crypto API", "description": "bitcoin", "tags": []},
        ])
        result = client.search_services("weather")
        assert len(result) == 1
        assert result[0]["name"] == "Weather API"

    def test_matches_by_description(self, client):
        self._patch_discover(client, [
            {"name": "Misc API", "description": "get crypto prices", "tags": []},
        ])
        result = client.search_services("crypto")
        assert len(result) == 1

    def test_matches_by_tag(self, client):
        self._patch_discover(client, [
            {"name": "XYZ API", "description": "nothing", "tags": ["weather", "climate"]},
        ])
        result = client.search_services("climate")
        assert len(result) == 1

    def test_case_insensitive(self, client):
        self._patch_discover(client, [
            {"name": "WEATHER API", "description": "", "tags": []},
        ])
        result = client.search_services("weather")
        assert len(result) == 1

    def test_no_results(self, client):
        self._patch_discover(client, [
            {"name": "Weather API", "description": "", "tags": []},
        ])
        result = client.search_services("zzznomatch")
        assert result == []

    def test_propagates_discover_exception(self, client):
        client.discover_services = MagicMock(side_effect=requests.RequestException("err"))
        with pytest.raises(requests.RequestException):
            client.search_services("test")


# ---------------------------------------------------------------------------
# get_marketplace_info
# ---------------------------------------------------------------------------

class TestGetMarketplaceInfo:
    @pytest.fixture
    def client(self):
        return X402Client()

    def test_json_response(self, client):
        data = {"name": "x402 Bazaar", "version": "1.0"}
        resp = _mock_response(200, json_data=data)
        client.session.get = MagicMock(return_value=resp)

        result = client.get_marketplace_info()
        assert result == data

    def test_html_fallback_on_json_decode_error(self, client):
        resp = _mock_response(200, text="<html>hello</html>")
        client.session.get = MagicMock(return_value=resp)

        result = client.get_marketplace_info()
        assert result["name"] == "x402 Bazaar"
        assert result["status"] == "online"
        assert "html" in result

    def test_html_truncated_to_500_chars(self, client):
        long_text = "x" * 1000
        resp = _mock_response(200, text=long_text)
        client.session.get = MagicMock(return_value=resp)

        result = client.get_marketplace_info()
        assert len(result["html"]) == 500

    def test_raises_on_request_exception(self, client):
        client.session.get = MagicMock(side_effect=requests.RequestException("fail"))
        with pytest.raises(requests.RequestException):
            client.get_marketplace_info()

    def test_raises_on_http_error(self, client):
        resp = _mock_response(503, raise_for_status=requests.HTTPError("503"))
        client.session.get = MagicMock(return_value=resp)
        with pytest.raises(requests.HTTPError):
            client.get_marketplace_info()


# ---------------------------------------------------------------------------
# call_api — status codes and branches
# ---------------------------------------------------------------------------

class TestCallApi:
    @pytest.fixture
    def client(self):
        return X402Client()

    # --- 200 OK ---

    def test_200_json_response(self, client):
        data = {"temperature": 20}
        resp = _mock_response(200, json_data=data)
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather", {"city": "Paris"})
        assert result["success"] is True
        assert result["data"] == data
        assert result["payment_status"] == "free"

    def test_200_with_payment_tx_hash(self, client):
        resp = _mock_response(200, json_data={"ok": True})
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather", payment_tx_hash="0xabc")
        assert result["success"] is True
        assert result["payment_status"] == "completed"

    def test_200_json_decode_error_falls_back_to_text(self, client):
        resp = _mock_response(200, text="plain text response")
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/test")
        assert result["success"] is True
        assert result["data"] == {"text": "plain text response"}

    # --- GET request headers ---

    def test_get_passes_params(self, client):
        resp = _mock_response(200, json_data={})
        client.session.get = MagicMock(return_value=resp)

        client.call_api("/api/weather", {"city": "London"})
        _, kwargs = client.session.get.call_args
        assert kwargs["params"] == {"city": "London"}

    def test_get_includes_payment_headers(self, client):
        resp = _mock_response(200, json_data={})
        client.session.get = MagicMock(return_value=resp)

        client.call_api("/api/weather", payment_tx_hash="0xdeadbeef")
        _, kwargs = client.session.get.call_args
        assert kwargs["headers"]["X-Payment-TxHash"] == "0xdeadbeef"
        assert kwargs["headers"]["X-Payment-Chain"] == "base"

    def test_get_no_payment_headers_when_no_tx(self, client):
        resp = _mock_response(200, json_data={})
        client.session.get = MagicMock(return_value=resp)

        client.call_api("/api/test")
        _, kwargs = client.session.get.call_args
        assert kwargs["headers"] == {}

    # --- POST ---

    def test_post_method_uses_session_post(self, client):
        resp = _mock_response(200, json_data={"url": "img.png"})
        client.session.post = MagicMock(return_value=resp)

        result = client.call_api("/api/image", {"prompt": "cat"}, method="POST")
        assert result["success"] is True
        client.session.post.assert_called_once()

    def test_post_sends_json_body(self, client):
        resp = _mock_response(200, json_data={})
        client.session.post = MagicMock(return_value=resp)

        client.call_api("/api/image", {"prompt": "dog"}, method="POST")
        _, kwargs = client.session.post.call_args
        assert kwargs["json"] == {"prompt": "dog"}

    # --- Unsupported method ---

    def test_unsupported_method_returns_error(self, client):
        result = client.call_api("/api/test", method="DELETE")
        assert result["success"] is False
        assert "Unsupported HTTP method" in result["error"]

    def test_put_also_unsupported(self, client):
        result = client.call_api("/api/test", method="PUT")
        assert result["success"] is False

    # --- 402 Payment Required ---

    def test_402_returns_payment_required(self, client):
        payment = {"amount": "0.01", "address": "0xABC"}
        resp = _mock_response(402, json_data=payment)
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["success"] is False
        assert result["payment_required"] is True
        assert "payment_details" in result

    def test_402_payment_details_has_instructions(self, client):
        resp = _mock_response(402, json_data={"amount": "0.05"})
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        details = result["payment_details"]
        assert "instructions" in details
        assert isinstance(details["instructions"], list)
        assert len(details["instructions"]) == 3

    def test_402_uses_required_payment_field(self, client):
        resp = _mock_response(402, json_data={"required_payment": "0.02"})
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["cost_usdc"] == "0.02"

    def test_402_fallback_when_json_decode_fails(self, client):
        resp = _mock_response(402, text="Payment Required")
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["payment_required"] is True
        details = result["payment_details"]
        assert details["address"] == X402Client.PAYMENT_ADDRESS

    def test_402_includes_correct_payment_address(self, client):
        resp = _mock_response(402, json_data={"amount": "0.01"})
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        details = result["payment_details"]
        assert details["payment_address"] == X402Client.PAYMENT_ADDRESS
        assert details["payment_chain"] == X402Client.PAYMENT_CHAIN
        assert details["payment_token"] == "USDC"

    # --- 400 Bad Request ---

    def test_400_returns_error_from_json(self, client):
        resp = _mock_response(400, json_data={"error": "missing city param"})
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["success"] is False
        assert result["error"] == "missing city param"

    def test_400_fallback_to_text_when_no_json(self, client):
        resp = _mock_response(400, text="Bad Request")
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["success"] is False
        assert result["error"] == "Bad Request"

    def test_400_default_error_when_no_error_key(self, client):
        resp = _mock_response(400, json_data={"message": "oops"})
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["error"] == "Bad request"

    # --- 429 Rate Limit ---

    def test_429_returns_rate_limit_error(self, client):
        resp = _mock_response(429)
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["success"] is False
        assert "Rate limit" in result["error"]

    # --- 500 Server Error ---

    def test_500_returns_server_error(self, client):
        resp = _mock_response(500)
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["success"] is False
        assert "Server error" in result["error"]

    # --- Other status codes ---

    def test_other_status_with_json_error_key(self, client):
        resp = _mock_response(503, json_data={"error": "service unavailable"})
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["success"] is False
        assert result["error"] == "service unavailable"

    def test_other_status_fallback_to_http_code(self, client):
        resp = _mock_response(418, text="I'm a teapot")
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert result["success"] is False
        assert "418" in result["error"]

    def test_other_status_text_truncated_to_200(self, client):
        resp = _mock_response(418, text="x" * 500)
        client.session.get = MagicMock(return_value=resp)

        result = client.call_api("/api/weather")
        assert len(result["error"]) <= 210  # "HTTP 418: " + 200 chars

    # --- Timeout ---

    def test_timeout_returns_error(self, client):
        client.session.get = MagicMock(side_effect=requests.Timeout())

        result = client.call_api("/api/weather")
        assert result["success"] is False
        assert "timeout" in result["error"].lower()
        assert str(client.timeout) in result["error"]

    # --- RequestException ---

    def test_request_exception_returns_error(self, client):
        client.session.get = MagicMock(side_effect=requests.RequestException("conn refused"))

        result = client.call_api("/api/weather")
        assert result["success"] is False
        assert "conn refused" in result["error"]

    # --- URL construction ---

    def test_url_built_from_base_url(self, client):
        resp = _mock_response(200, json_data={})
        client.session.get = MagicMock(return_value=resp)

        client.call_api("/api/test")
        args, _ = client.session.get.call_args
        assert args[0] == "https://x402-api.onrender.com/api/test"


# ---------------------------------------------------------------------------
# get_service_details
# ---------------------------------------------------------------------------

class TestGetServiceDetails:
    @pytest.fixture
    def client(self):
        return X402Client()

    def test_returns_matching_service(self, client):
        services = [
            {"name": "Weather API", "endpoint": "/api/weather"},
            {"name": "Crypto API", "endpoint": "/api/crypto"},
        ]
        client.discover_services = MagicMock(return_value=services)

        result = client.get_service_details("Weather API")
        assert result == services[0]

    def test_case_insensitive_match(self, client):
        services = [{"name": "Weather API", "endpoint": "/api/weather"}]
        client.discover_services = MagicMock(return_value=services)

        result = client.get_service_details("weather api")
        assert result["name"] == "Weather API"

    def test_returns_none_when_not_found(self, client):
        client.discover_services = MagicMock(return_value=[
            {"name": "Crypto API", "endpoint": "/api/crypto"},
        ])
        result = client.get_service_details("Nonexistent API")
        assert result is None

    def test_returns_none_on_exception(self, client):
        client.discover_services = MagicMock(side_effect=Exception("boom"))
        result = client.get_service_details("Weather API")
        assert result is None

    def test_returns_none_on_empty_services(self, client):
        client.discover_services = MagicMock(return_value=[])
        result = client.get_service_details("Weather API")
        assert result is None


# ---------------------------------------------------------------------------
# test_connection
# ---------------------------------------------------------------------------

class TestTestConnection:
    @pytest.fixture
    def client(self):
        return X402Client()

    @pytest.mark.parametrize("status_code", [200, 402, 400])
    def test_returns_true_for_expected_codes(self, client, status_code):
        resp = _mock_response(status_code)
        client.session.get = MagicMock(return_value=resp)
        assert client.test_connection() is True

    @pytest.mark.parametrize("status_code", [500, 503, 404])
    def test_returns_false_for_unexpected_codes(self, client, status_code):
        resp = _mock_response(status_code)
        client.session.get = MagicMock(return_value=resp)
        assert client.test_connection() is False

    def test_returns_false_on_exception(self, client):
        client.session.get = MagicMock(side_effect=requests.ConnectionError("refused"))
        assert client.test_connection() is False

    def test_uses_base_url(self, client):
        resp = _mock_response(200)
        client.session.get = MagicMock(return_value=resp)
        client.test_connection()
        args, kwargs = client.session.get.call_args
        assert args[0] == "https://x402-api.onrender.com/"


# ---------------------------------------------------------------------------
# get_public_stats
# ---------------------------------------------------------------------------

class TestGetPublicStats:
    @pytest.fixture
    def client(self):
        return X402Client()

    def test_success_returns_stats(self, client):
        stats = {"services": {"total": 70}, "calls": 1000}
        resp = _mock_response(200, json_data=stats)
        client.session.get = MagicMock(return_value=resp)

        result = client.get_public_stats()
        assert result == stats

    def test_calls_correct_endpoint(self, client):
        resp = _mock_response(200, json_data={})
        client.session.get = MagicMock(return_value=resp)

        client.get_public_stats()
        args, _ = client.session.get.call_args
        assert args[0] == "https://x402-api.onrender.com/api/public-stats"

    def test_raises_on_request_exception(self, client):
        client.session.get = MagicMock(side_effect=requests.RequestException("fail"))
        with pytest.raises(requests.RequestException):
            client.get_public_stats()

    def test_raises_on_http_error(self, client):
        resp = _mock_response(503, raise_for_status=requests.HTTPError("503"))
        client.session.get = MagicMock(return_value=resp)
        with pytest.raises(requests.HTTPError):
            client.get_public_stats()


# ---------------------------------------------------------------------------
# Convenience methods
# ---------------------------------------------------------------------------

class TestConvenienceMethods:
    @pytest.fixture
    def client(self):
        return X402Client()

    def _patch_call_api(self, client, return_value=None):
        if return_value is None:
            return_value = {"success": True, "data": {}}
        client.call_api = MagicMock(return_value=return_value)

    def test_call_weather_api(self, client):
        self._patch_call_api(client)
        client.call_weather_api("Paris")
        client.call_api.assert_called_once_with(
            "/api/weather", {"city": "Paris"}, payment_tx_hash=None
        )

    def test_call_weather_api_with_tx(self, client):
        self._patch_call_api(client)
        client.call_weather_api("Tokyo", payment_tx_hash="0xabc")
        client.call_api.assert_called_once_with(
            "/api/weather", {"city": "Tokyo"}, payment_tx_hash="0xabc"
        )

    def test_call_search_api(self, client):
        self._patch_call_api(client)
        client.call_search_api("bitcoin")
        client.call_api.assert_called_once_with(
            "/api/search", {"q": "bitcoin"}, payment_tx_hash=None
        )

    def test_call_search_api_with_tx(self, client):
        self._patch_call_api(client)
        client.call_search_api("eth", payment_tx_hash="0xdef")
        client.call_api.assert_called_once_with(
            "/api/search", {"q": "eth"}, payment_tx_hash="0xdef"
        )

    def test_call_crypto_api(self, client):
        self._patch_call_api(client)
        client.call_crypto_api("BTC")
        client.call_api.assert_called_once_with(
            "/api/crypto", {"symbol": "BTC"}, payment_tx_hash=None
        )

    def test_call_crypto_api_with_tx(self, client):
        self._patch_call_api(client)
        client.call_crypto_api("ETH", payment_tx_hash="0x111")
        client.call_api.assert_called_once_with(
            "/api/crypto", {"symbol": "ETH"}, payment_tx_hash="0x111"
        )

    def test_call_image_api(self, client):
        self._patch_call_api(client)
        client.call_image_api("a cat")
        client.call_api.assert_called_once_with(
            "/api/image", {"prompt": "a cat"}, method="POST", payment_tx_hash=None
        )

    def test_call_image_api_with_tx(self, client):
        self._patch_call_api(client)
        client.call_image_api("dog", payment_tx_hash="0x222")
        client.call_api.assert_called_once_with(
            "/api/image", {"prompt": "dog"}, method="POST", payment_tx_hash="0x222"
        )

    def test_call_scraper_api(self, client):
        self._patch_call_api(client)
        client.call_scraper_api("https://example.com")
        client.call_api.assert_called_once_with(
            "/api/scrape", {"url": "https://example.com"}, payment_tx_hash=None
        )

    def test_call_scraper_api_with_tx(self, client):
        self._patch_call_api(client)
        client.call_scraper_api("https://foo.bar", payment_tx_hash="0x333")
        client.call_api.assert_called_once_with(
            "/api/scrape", {"url": "https://foo.bar"}, payment_tx_hash="0x333"
        )

    def test_convenience_methods_return_call_api_result(self, client):
        expected = {"success": True, "data": {"temp": 22}}
        self._patch_call_api(client, return_value=expected)

        assert client.call_weather_api("Paris") == expected
        assert client.call_search_api("q") == expected
        assert client.call_crypto_api("BTC") == expected
        assert client.call_image_api("img") == expected
        assert client.call_scraper_api("url") == expected
