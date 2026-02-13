"""
x402 Bazaar HTTP Client

Handles API discovery, search, and x402 payment protocol for x402 Bazaar marketplace.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
import requests


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class X402Client:
    """
    HTTP client for x402 Bazaar marketplace.

    Handles service discovery, API calls, and x402 payment protocol.
    """

    BASE_URL = "https://x402-api.onrender.com"
    TIMEOUT = 30  # seconds
    PAYMENT_ADDRESS = "0xfb1c478BD5567BdcD39782E0D6D23418bFda2430"
    PAYMENT_CHAIN = "base"

    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize x402 client.

        Args:
            base_url: Optional custom base URL (default: production URL)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "x402-autogpt-plugin/0.1.0",
            "Accept": "application/json",
        })
        logger.info(f"X402Client initialized with base URL: {self.base_url}")

    def discover_services(self) -> List[Dict[str, Any]]:
        """
        Discover all available services on x402 Bazaar.

        Returns:
            List of service objects with name, description, cost, etc.

        Raises:
            requests.RequestException: If the request fails
        """
        try:
            url = f"{self.base_url}/api/services"
            logger.info(f"Discovering services from {url}")

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            services = response.json()
            logger.info(f"Discovered {len(services)} services")

            return services

        except requests.RequestException as e:
            logger.error(f"Error discovering services: {str(e)}")
            raise

    def search_services(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for services by keyword (client-side filtering of free /api/services).

        Args:
            query: Search keyword

        Returns:
            List of matching service objects
        """
        try:
            logger.info(f"Searching services with query: {query}")
            services = self.discover_services()
            q = query.lower()
            results = [
                svc for svc in services
                if q in svc.get("name", "").lower()
                or q in svc.get("description", "").lower()
                or any(q in tag.lower() for tag in svc.get("tags", []))
            ]
            logger.info(f"Found {len(results)} services matching '{query}'")
            return results

        except Exception as e:
            logger.error(f"Error searching services: {str(e)}")
            raise

    def get_marketplace_info(self) -> Dict[str, Any]:
        """
        Get information about the x402 Bazaar marketplace.

        Returns:
            Marketplace information object

        Raises:
            requests.RequestException: If the request fails
        """
        try:
            url = f"{self.base_url}/"
            logger.info("Fetching marketplace info")

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Try to parse as JSON, fallback to text
            try:
                info = response.json()
            except json.JSONDecodeError:
                info = {
                    "name": "x402 Bazaar",
                    "status": "online",
                    "html": response.text[:500],
                }

            logger.info("Marketplace info retrieved successfully")
            return info

        except requests.RequestException as e:
            logger.error(f"Error getting marketplace info: {str(e)}")
            raise

    def call_api(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = "GET",
        payment_tx_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Call an API endpoint on x402 Bazaar.

        Handles x402 payment protocol:
        1. Call endpoint without payment -> receive 402 Payment Required
        2. Extract payment details (amount, address, chain)
        3. Return payment instructions to user
        4. If payment_tx_hash provided, retry with payment headers

        Args:
            endpoint: API endpoint path (e.g., '/api/weather')
            params: Query parameters (GET) or request body (POST)
            method: HTTP method ('GET' or 'POST')
            payment_tx_hash: Optional transaction hash if payment already made

        Returns:
            Dict with:
                - success: bool
                - data: API response data (if successful)
                - payment_required: bool (if payment needed)
                - payment_details: Payment info (if 402 received)
                - error: Error message (if failed)

        Raises:
            requests.RequestException: If the request fails unexpectedly
        """
        try:
            url = f"{self.base_url}{endpoint}"
            logger.info(f"Calling {method} {url}")

            # Prepare request
            headers = {}
            if payment_tx_hash:
                headers["X-Payment-TxHash"] = payment_tx_hash
                headers["X-Payment-Chain"] = self.PAYMENT_CHAIN
                logger.info(f"Including payment headers with tx: {payment_tx_hash}")

            # Make request
            if method.upper() == "GET":
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            elif method.upper() == "POST":
                response = self.session.post(
                    url,
                    json=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported HTTP method: {method}",
                }

            # Handle response
            if response.status_code == 200:
                logger.info("API call successful (200 OK)")
                try:
                    data = response.json()
                except json.JSONDecodeError:
                    data = {"text": response.text}

                return {
                    "success": True,
                    "data": data,
                    "payment_status": "completed" if payment_tx_hash else "free",
                }

            elif response.status_code == 402:
                # Payment Required - extract payment details
                logger.info("Payment required (402)")

                try:
                    payment_details = response.json()
                except json.JSONDecodeError:
                    payment_details = {
                        "amount": "unknown",
                        "address": self.PAYMENT_ADDRESS,
                        "chain": self.PAYMENT_CHAIN,
                    }

                # Add helpful instructions
                cost_usdc = payment_details.get("amount", payment_details.get("required_payment", "unknown"))

                instructions = {
                    "message": f"Payment required: {cost_usdc} USDC",
                    "instructions": [
                        f"1. Send {cost_usdc} USDC on {self.PAYMENT_CHAIN.upper()} to: {self.PAYMENT_ADDRESS}",
                        "2. Wait for transaction confirmation",
                        "3. Call this endpoint again with transaction hash",
                    ],
                    "payment_address": self.PAYMENT_ADDRESS,
                    "payment_chain": self.PAYMENT_CHAIN,
                    "payment_token": "USDC",
                    "payment_amount": cost_usdc,
                }

                return {
                    "success": False,
                    "payment_required": True,
                    "payment_details": {**payment_details, **instructions},
                    "cost_usdc": cost_usdc,
                }

            elif response.status_code == 400:
                # Bad request - extract error message
                logger.warning(f"Bad request (400)")
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", "Bad request")
                except json.JSONDecodeError:
                    error_msg = response.text

                return {
                    "success": False,
                    "error": error_msg,
                }

            elif response.status_code == 429:
                # Rate limited
                logger.warning("Rate limited (429)")
                return {
                    "success": False,
                    "error": "Rate limit exceeded. Please try again later.",
                }

            elif response.status_code == 500:
                # Server error
                logger.error("Server error (500)")
                return {
                    "success": False,
                    "error": "Server error. Please try again later.",
                }

            else:
                # Other error
                logger.error(f"Unexpected status code: {response.status_code}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", f"HTTP {response.status_code}")
                except json.JSONDecodeError:
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"

                return {
                    "success": False,
                    "error": error_msg,
                }

        except requests.Timeout:
            logger.error("Request timeout")
            return {
                "success": False,
                "error": f"Request timeout after {self.timeout} seconds",
            }

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
            }

    def get_service_details(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific service by name.

        Args:
            service_name: Name of the service (e.g., 'Weather API')

        Returns:
            Service object if found, None otherwise
        """
        try:
            services = self.discover_services()
            for svc in services:
                if svc.get("name", "").lower() == service_name.lower():
                    return svc
            return None

        except Exception as e:
            logger.error(f"Error getting service details: {str(e)}")
            return None

    def test_connection(self) -> bool:
        """
        Test connection to x402 Bazaar marketplace.

        Returns:
            True if marketplace is reachable, False otherwise
        """
        try:
            response = self.session.get(
                f"{self.base_url}/",
                timeout=self.timeout,
            )
            return response.status_code in [200, 402, 400]

        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    def get_public_stats(self) -> Dict[str, Any]:
        """
        Get public marketplace statistics.

        Returns:
            Statistics object with service count, API calls, etc.
        """
        try:
            url = f"{self.base_url}/api/public-stats"
            logger.info("Fetching public stats")

            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            stats = response.json()
            logger.info("Public stats retrieved successfully")

            return stats

        except requests.RequestException as e:
            logger.error(f"Error getting public stats: {str(e)}")
            raise

    def call_weather_api(self, city: str, payment_tx_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Convenience method to call Weather API.

        Args:
            city: City name
            payment_tx_hash: Optional transaction hash if payment already made

        Returns:
            Weather data or payment details
        """
        return self.call_api("/api/weather", {"city": city}, payment_tx_hash=payment_tx_hash)

    def call_search_api(self, query: str, payment_tx_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Convenience method to call Web Search API.

        Args:
            query: Search query
            payment_tx_hash: Optional transaction hash if payment already made

        Returns:
            Search results or payment details
        """
        return self.call_api("/api/search", {"q": query}, payment_tx_hash=payment_tx_hash)

    def call_crypto_api(self, symbol: str, payment_tx_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Convenience method to call Crypto Price API.

        Args:
            symbol: Crypto symbol (e.g., 'BTC')
            payment_tx_hash: Optional transaction hash if payment already made

        Returns:
            Crypto price data or payment details
        """
        return self.call_api("/api/crypto", {"symbol": symbol}, payment_tx_hash=payment_tx_hash)

    def call_image_api(self, prompt: str, payment_tx_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Convenience method to call AI Image Generation API.

        Args:
            prompt: Image generation prompt
            payment_tx_hash: Optional transaction hash if payment already made

        Returns:
            Generated image URL or payment details
        """
        return self.call_api("/api/image", {"prompt": prompt}, method="POST", payment_tx_hash=payment_tx_hash)

    def call_scraper_api(self, url: str, payment_tx_hash: Optional[str] = None) -> Dict[str, Any]:
        """
        Convenience method to call URL Scraper API.

        Args:
            url: URL to scrape
            payment_tx_hash: Optional transaction hash if payment already made

        Returns:
            Scraped content or payment details
        """
        return self.call_api("/api/scrape", {"url": url}, payment_tx_hash=payment_tx_hash)
