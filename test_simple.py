"""
Simple test script to verify X402Client works without Auto-GPT dependencies
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import only the client (no plugin)
from x402_bazaar.x402_client import X402Client


def main():
    print("=== Testing X402Client ===\n")

    # Initialize client
    client = X402Client()
    print(f"Client initialized: {client.base_url}\n")

    # Test 1: Connection
    print("1. Testing connection...")
    try:
        is_connected = client.test_connection()
        print(f"   Connection: {'OK' if is_connected else 'FAILED'}\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # Test 2: Discover services
    print("2. Discovering services...")
    try:
        services = client.discover_services()
        print(f"   Found {len(services)} services\n")

        # Show first 3
        for svc in services[:3]:
            print(f"   - {svc.get('name', 'Unknown')}: {svc.get('cost_usdc', 'Free')} USDC")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")

    # Test 3: Search services
    print("3. Searching for 'weather' APIs...")
    try:
        results = client.search_services("weather")
        print(f"   Found {len(results)} results\n")

        for result in results[:2]:
            print(f"   - {result.get('name', 'Unknown')}")
            print(f"     {result.get('description', 'No description')}")
        print()
    except Exception as e:
        print(f"   Error: {e}\n")

    # Test 4: Call weather API (will require payment)
    print("4. Calling Weather API (will require payment)...")
    try:
        result = client.call_weather_api("Paris")

        if result.get("success"):
            print("   Success! Data received:")
            print(f"   {result['data']}\n")
        elif result.get("payment_required"):
            print("   Payment required (expected):")
            print(f"   Amount: {result.get('cost_usdc', 'unknown')} USDC")
            print(f"   Address: {result['payment_details']['payment_address']}")
            print(f"   Chain: {result['payment_details']['payment_chain']}\n")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    # Test 5: Get public stats
    print("5. Getting public stats...")
    try:
        stats = client.get_public_stats()
        print(f"   Services: {stats.get('services', {}).get('total', 'N/A')}")
        print(f"   API Calls: {stats.get('apiCalls', {}).get('total', 'N/A')}")
        print(f"   Integrations: {stats.get('integrations', {}).get('total', 'N/A')}\n")
    except Exception as e:
        print(f"   Error: {e}\n")

    print("=== All Tests Complete ===")


if __name__ == "__main__":
    main()
