"""
Unit tests for X402Client

These tests verify the client's functionality against the live x402 Bazaar API.
"""

import pytest
from x402_bazaar.x402_client import X402Client


class TestX402Client:
    """Test suite for X402Client."""

    @pytest.fixture
    def client(self):
        """Create a client instance for testing."""
        return X402Client()

    def test_client_initialization(self, client):
        """Test that client initializes with correct defaults."""
        assert client.base_url == "https://x402-api.onrender.com"
        assert client.timeout == 30
        assert client.PAYMENT_ADDRESS == "0xfb1c478BD5567BdcD39782E0D6D23418bFda2430"
        assert client.PAYMENT_CHAIN == "base"

    def test_client_custom_url(self):
        """Test client with custom base URL."""
        custom_url = "http://localhost:3000"
        client = X402Client(base_url=custom_url)
        assert client.base_url == custom_url

    def test_client_custom_timeout(self):
        """Test client with custom timeout."""
        client = X402Client(timeout=60)
        assert client.timeout == 60

    def test_discover_services(self, client):
        """Test service discovery."""
        services = client.discover_services()

        assert isinstance(services, list)
        assert len(services) > 0

        # Check first service has required fields
        service = services[0]
        assert "name" in service
        assert "description" in service
        assert "endpoint" in service

    def test_search_services(self, client):
        """Test service search."""
        results = client.search_services("weather")

        assert isinstance(results, list)
        assert len(results) > 0

        # All results should contain "weather" in name or description
        for result in results:
            name = result.get("name", "").lower()
            desc = result.get("description", "").lower()
            assert "weather" in name or "weather" in desc

    def test_search_services_crypto(self, client):
        """Test searching for crypto APIs."""
        results = client.search_services("crypto")

        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_services_no_results(self, client):
        """Test search with no results."""
        results = client.search_services("xyzabc123nonexistent")

        assert isinstance(results, list)
        # May return empty list or still return results

    def test_get_marketplace_info(self, client):
        """Test getting marketplace info."""
        info = client.get_marketplace_info()

        assert isinstance(info, dict)
        # Should have some data
        assert len(info) > 0

    def test_call_api_free_endpoint(self, client):
        """Test calling a free endpoint."""
        # /api/services is free
        result = client.call_api("/api/services")

        assert isinstance(result, dict)
        if result.get("success"):
            assert "data" in result
            assert isinstance(result["data"], list)

    def test_call_api_payment_required(self, client):
        """Test calling a paid endpoint triggers payment requirement."""
        # Weather API requires payment
        result = client.call_weather_api("Paris")

        assert isinstance(result, dict)

        # Should require payment (unless we have a valid payment)
        if result.get("payment_required"):
            assert "payment_details" in result
            assert "payment_address" in result["payment_details"]
            assert "payment_amount" in result["payment_details"]
            assert "payment_chain" in result["payment_details"]
            assert result["payment_details"]["payment_address"] == client.PAYMENT_ADDRESS
            assert result["payment_details"]["payment_chain"] == client.PAYMENT_CHAIN

    def test_call_api_invalid_endpoint(self, client):
        """Test calling an invalid endpoint."""
        result = client.call_api("/api/nonexistent123")

        assert isinstance(result, dict)
        assert result.get("success") is False
        # Should have error message

    def test_get_service_details(self, client):
        """Test getting details for a specific service."""
        # Search for a known service
        services = client.discover_services()
        if services:
            service_name = services[0]["name"]
            details = client.get_service_details(service_name)

            assert details is not None
            assert details["name"] == service_name

    def test_get_service_details_not_found(self, client):
        """Test getting details for non-existent service."""
        details = client.get_service_details("Nonexistent API xyz123")
        assert details is None

    def test_test_connection(self, client):
        """Test connection to marketplace."""
        is_connected = client.test_connection()
        assert is_connected is True

    def test_get_public_stats(self, client):
        """Test getting public statistics."""
        stats = client.get_public_stats()

        assert isinstance(stats, dict)
        # Should have stats data
        if "services" in stats:
            assert isinstance(stats["services"], dict)

    def test_convenience_method_search(self, client):
        """Test convenience method for search API."""
        result = client.call_search_api("bitcoin")

        assert isinstance(result, dict)
        # Should require payment or return data

    def test_convenience_method_crypto(self, client):
        """Test convenience method for crypto API."""
        result = client.call_crypto_api("BTC")

        assert isinstance(result, dict)
        # Should require payment or return data

    def test_convenience_method_image(self, client):
        """Test convenience method for image API."""
        result = client.call_image_api("a beautiful sunset")

        assert isinstance(result, dict)
        # Should require payment or return data

    def test_convenience_method_scraper(self, client):
        """Test convenience method for scraper API."""
        result = client.call_scraper_api("https://example.com")

        assert isinstance(result, dict)
        # Should require payment or return data

    def test_call_api_with_params(self, client):
        """Test calling API with query parameters."""
        result = client.call_api("/api/weather", {"city": "London"})

        assert isinstance(result, dict)
        # Should work (either payment required or success)

    def test_call_api_post_method(self, client):
        """Test calling API with POST method."""
        result = client.call_api(
            "/api/image",
            {"prompt": "test image"},
            method="POST"
        )

        assert isinstance(result, dict)
        # Should require payment

    def test_call_api_invalid_method(self, client):
        """Test calling API with invalid HTTP method."""
        result = client.call_api("/api/weather", method="DELETE")

        assert isinstance(result, dict)
        assert result.get("success") is False
        assert "Unsupported HTTP method" in result.get("error", "")

    def test_payment_details_structure(self, client):
        """Test that payment details have correct structure."""
        result = client.call_weather_api("Paris")

        if result.get("payment_required"):
            details = result["payment_details"]

            # Check all required fields
            assert "payment_address" in details
            assert "payment_chain" in details
            assert "payment_token" in details
            assert "payment_amount" in details
            assert "message" in details
            assert "instructions" in details

            # Check types
            assert isinstance(details["instructions"], list)
            assert len(details["instructions"]) > 0

    def test_error_handling_timeout(self):
        """Test timeout handling."""
        client = X402Client(timeout=0.001)  # Very short timeout

        result = client.call_api("/api/weather", {"city": "Paris"})

        assert isinstance(result, dict)
        # Should handle timeout gracefully

    def test_session_headers(self, client):
        """Test that session has correct headers."""
        assert "User-Agent" in client.session.headers
        assert "x402-autogpt-plugin" in client.session.headers["User-Agent"]
        assert "Accept" in client.session.headers
        assert client.session.headers["Accept"] == "application/json"


class TestX402ClientIntegration:
    """Integration tests that verify real API behavior."""

    @pytest.fixture
    def client(self):
        """Create a client instance for testing."""
        return X402Client()

    def test_full_discovery_flow(self, client):
        """Test complete service discovery flow."""
        # 1. Get all services
        all_services = client.discover_services()
        assert len(all_services) > 0

        # 2. Search for specific category
        weather_services = client.search_services("weather")
        assert len(weather_services) > 0

        # 3. Get details for first result
        if weather_services:
            service_name = weather_services[0]["name"]
            details = client.get_service_details(service_name)
            assert details is not None
            assert details["name"] == service_name

    def test_payment_flow_simulation(self, client):
        """Test simulated payment flow (without actual payment)."""
        # 1. Call paid API without payment
        result1 = client.call_weather_api("Tokyo")

        if result1.get("payment_required"):
            # 2. Extract payment details
            details = result1["payment_details"]
            assert details["payment_address"]
            assert details["payment_amount"]

            # 3. Simulate retry with fake tx hash (will fail verification)
            fake_tx = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
            result2 = client.call_weather_api("Tokyo", payment_tx_hash=fake_tx)

            # Should return error (invalid transaction)
            assert isinstance(result2, dict)
            # Error expected since payment wasn't real

    def test_multiple_api_calls(self, client):
        """Test calling multiple different APIs."""
        apis = [
            ("/api/weather", {"city": "Paris"}),
            ("/api/crypto", {"symbol": "BTC"}),
            ("/api/search", {"q": "bitcoin"}),
        ]

        for endpoint, params in apis:
            result = client.call_api(endpoint, params)
            assert isinstance(result, dict)
            # Each should either require payment or succeed

    def test_marketplace_status(self, client):
        """Test that marketplace is online and functional."""
        # Test connection
        assert client.test_connection() is True

        # Get stats
        stats = client.get_public_stats()
        assert isinstance(stats, dict)

        # Get services
        services = client.discover_services()
        assert len(services) > 0

        # Get info
        info = client.get_marketplace_info()
        assert isinstance(info, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
