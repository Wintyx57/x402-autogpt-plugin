"""
Standalone usage example for x402 Bazaar client

This example demonstrates how to use the X402Client directly
without Auto-GPT integration.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from x402_bazaar.x402_client import X402Client


def main():
    """Main example function."""
    print("=== x402 Bazaar Client - Standalone Example ===\n")

    # Initialize client
    client = X402Client()
    print(f"Client initialized with base URL: {client.base_url}\n")

    # Example 1: Test connection
    print("1. Testing connection...")
    is_connected = client.test_connection()
    print(f"   Connection: {'OK' if is_connected else 'FAILED'}\n")

    if not is_connected:
        print("Cannot connect to marketplace. Exiting.")
        return

    # Example 2: Get marketplace stats
    print("2. Getting marketplace statistics...")
    try:
        stats = client.get_public_stats()
        print(f"   Total services: {stats.get('services', {}).get('total', 'N/A')}")
        print(f"   API calls: {stats.get('apiCalls', {}).get('total', 'N/A')}")
        print(f"   Integrations: {stats.get('integrations', {}).get('total', 'N/A')}\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # Example 3: Discover all services
    print("3. Discovering all services...")
    try:
        services = client.discover_services()
        print(f"   Found {len(services)} APIs\n")

        # Show first 5 services
        print("   First 5 services:")
        for i, svc in enumerate(services[:5], 1):
            name = svc.get("name", "Unknown")
            cost = svc.get("cost_usdc", "Free")
            print(f"   {i}. {name} - {cost} USDC")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")

    # Example 4: Search for weather APIs
    print("4. Searching for 'weather' APIs...")
    try:
        results = client.search_services("weather")
        print(f"   Found {len(results)} weather-related APIs\n")

        for result in results:
            name = result.get("name", "Unknown")
            desc = result.get("description", "No description")
            endpoint = result.get("endpoint", "N/A")
            cost = result.get("cost_usdc", "Free")
            print(f"   • {name}")
            print(f"     Description: {desc}")
            print(f"     Endpoint: {endpoint}")
            print(f"     Cost: {cost} USDC\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # Example 5: Call a free API endpoint
    print("5. Calling free endpoint (/api/services)...")
    try:
        result = client.call_api("/api/services")
        if result.get("success"):
            data = result["data"]
            print(f"   Success! Received {len(data)} services\n")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # Example 6: Call a paid API (will require payment)
    print("6. Calling paid endpoint (Weather API for Paris)...")
    try:
        result = client.call_weather_api("Paris")

        if result.get("success"):
            # Payment already made (unlikely in this example)
            weather = result["data"]
            print(f"   Temperature: {weather.get('temperature', 'N/A')}°C")
            print(f"   Conditions: {weather.get('conditions', 'N/A')}\n")

        elif result.get("payment_required"):
            # Payment required - show instructions
            details = result["payment_details"]
            print(f"   Payment Required!")
            print(f"   Amount: {details['payment_amount']} USDC")
            print(f"   Address: {details['payment_address']}")
            print(f"   Chain: {details['payment_chain'].upper()}\n")
            print("   Instructions:")
            for instruction in details["instructions"]:
                print(f"   {instruction}")
            print()

            # Simulate payment flow (user would send USDC here)
            print("   To complete the payment flow:")
            print("   1. Send USDC on Base to the address above")
            print("   2. Get the transaction hash from BaseScan")
            print("   3. Call: result = client.call_weather_api('Paris', payment_tx_hash=tx_hash)")
            print("   4. Receive weather data\n")

        else:
            print(f"   Error: {result.get('error', 'Unknown error')}\n")

    except Exception as e:
        print(f"   Error: {e}\n")

    # Example 7: Get details for a specific service
    print("7. Getting details for 'Weather API'...")
    try:
        details = client.get_service_details("Weather API")
        if details:
            print(f"   Name: {details.get('name', 'N/A')}")
            print(f"   Description: {details.get('description', 'N/A')}")
            print(f"   Endpoint: {details.get('endpoint', 'N/A')}")
            print(f"   Cost: {details.get('cost_usdc', 'N/A')} USDC")
            print(f"   Category: {details.get('category', 'N/A')}\n")
        else:
            print("   Service not found\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # Example 8: Test other convenience methods
    print("8. Testing convenience methods...")

    # Crypto API
    print("   a) Crypto Price API (BTC)...")
    try:
        result = client.call_crypto_api("BTC")
        if result.get("payment_required"):
            print(f"      Payment required: {result['cost_usdc']} USDC")
        elif result.get("success"):
            print(f"      Success! Data received")
    except Exception as e:
        print(f"      Error: {e}")

    # Search API
    print("   b) Web Search API (bitcoin)...")
    try:
        result = client.call_search_api("bitcoin")
        if result.get("payment_required"):
            print(f"      Payment required: {result['cost_usdc']} USDC")
        elif result.get("success"):
            print(f"      Success! Data received")
    except Exception as e:
        print(f"      Error: {e}")

    # Image API
    print("   c) AI Image Generation API...")
    try:
        result = client.call_image_api("a beautiful sunset")
        if result.get("payment_required"):
            print(f"      Payment required: {result['cost_usdc']} USDC")
        elif result.get("success"):
            print(f"      Success! Data received")
    except Exception as e:
        print(f"      Error: {e}")

    # Scraper API
    print("   d) URL Scraper API...")
    try:
        result = client.call_scraper_api("https://example.com")
        if result.get("payment_required"):
            print(f"      Payment required: {result['cost_usdc']} USDC")
        elif result.get("success"):
            print(f"      Success! Data received")
    except Exception as e:
        print(f"      Error: {e}")

    print("\n=== Example Complete ===")
    print("\nNext steps:")
    print("1. Install the plugin: pip install -e .")
    print("2. Add to Auto-GPT plugins directory")
    print("3. Enable in Auto-GPT configuration")
    print("4. Use x402 commands in Auto-GPT")
    print("\nDocumentation: https://github.com/x402-bazaar/x402-autogpt-plugin")


if __name__ == "__main__":
    main()
