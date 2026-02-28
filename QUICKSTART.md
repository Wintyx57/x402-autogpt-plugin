# Quick Start Guide

Get started with the x402 Bazaar Auto-GPT Plugin in 5 minutes.

## Installation

### Option 1: From Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/x402-bazaar/x402-autogpt-plugin.git
cd x402-autogpt-plugin

# Install in editable mode
pip install -e .
```

### Option 2: From PyPI (Coming Soon)

```bash
pip install x402-autogpt-plugin
```

## Setup for Auto-GPT

### 1. Add to Auto-GPT Plugins Directory

```bash
# Copy plugin to Auto-GPT plugins directory
cp -r src/x402_bazaar ~/.config/Auto-GPT/plugins/

# Or create a symbolic link (Linux/Mac)
ln -s $(pwd)/src/x402_bazaar ~/.config/Auto-GPT/plugins/x402_bazaar

# Windows (run as Administrator)
mklink /D "C:\Users\YourName\.config\Auto-GPT\plugins\x402_bazaar" "C:\path\to\x402-autogpt-plugin\src\x402_bazaar"
```

### 2. Enable Plugin in Auto-GPT

Edit `plugins_config.yaml`:

```yaml
x402-bazaar:
  enabled: true
```

Or enable via Auto-GPT CLI when prompted.

### 3. Verify Installation

```bash
# In Auto-GPT
> x402 info
```

You should see marketplace information.

## Standalone Usage (Without Auto-GPT)

You can use the client directly in Python:

```python
from x402_bazaar.x402_client import X402Client

# Initialize client
client = X402Client()

# Discover all APIs
services = client.discover_services()
print(f"Found {len(services)} APIs")

# Search for specific APIs
weather_apis = client.search_services("weather")
print(f"Found {len(weather_apis)} weather APIs")

# Call an API
result = client.call_weather_api("Paris")

if result.get("payment_required"):
    # Show payment instructions
    details = result["payment_details"]
    print(f"Send {details['payment_amount']} USDC to {details['payment_address']}")
    print(f"Chain: {details['payment_chain']}")

    # After payment, retry with transaction hash
    tx_hash = "0x123..."  # Your transaction hash
    result = client.call_weather_api("Paris", payment_tx_hash=tx_hash)

if result.get("success"):
    print(result["data"])
```

## First API Call

### Step 1: List Available APIs

```python
from x402_bazaar.x402_client import X402Client

client = X402Client()
services = client.discover_services()

for service in services[:5]:  # First 5
    print(f"{service['name']}: {service['cost_usdc']} USDC")
```

### Step 2: Call a Free API

```python
# Get all services (free endpoint)
result = client.call_api("/api/services")

if result["success"]:
    print(f"Success! Got {len(result['data'])} services")
```

### Step 3: Call a Paid API

```python
# Call Weather API (requires payment)
result = client.call_weather_api("Tokyo")

if result.get("payment_required"):
    print("Payment needed!")
    print(f"Amount: {result['cost_usdc']} USDC")
    print(f"Address: {result['payment_details']['payment_address']}")
    print(f"Chain: {result['payment_details']['payment_chain']}")
```

### Step 4: Make Payment

Send USDC on Base chain:
- **Token**: USDC (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`)
- **Chain**: Base (Coinbase L2)
- **To**: `0xfb1c478BD5567BdcD39782E0D6D23418bFda2430`
- **Amount**: From payment details (e.g., 0.005 USDC)

Use MetaMask, Coinbase Wallet, or any Base-compatible wallet.

### Step 5: Retry with Transaction Hash

```python
# After sending payment, get transaction hash from BaseScan
tx_hash = "0xYourTransactionHashHere"

# Retry API call with payment proof
result = client.call_weather_api("Tokyo", payment_tx_hash=tx_hash)

if result.get("success"):
    weather = result["data"]
    print(f"Temperature: {weather['temperature']}°C")
    print(f"Conditions: {weather['conditions']}")
```

## Common Tasks

### Search for APIs

```python
# Search by keyword
crypto_apis = client.search_services("crypto")
ai_apis = client.search_services("ai")
data_apis = client.search_services("data")

for api in crypto_apis:
    print(f"{api['name']}: {api['description']}")
```

### Get API Details

```python
# Get details for a specific service
details = client.get_service_details("Weather API")

if details:
    print(f"Name: {details['name']}")
    print(f"Endpoint: {details['endpoint']}")
    print(f"Cost: {details['cost_usdc']} USDC")
    print(f"Description: {details['description']}")
```

### Test Connection

```python
# Test if marketplace is reachable
if client.test_connection():
    print("Connected to x402 Bazaar!")
else:
    print("Cannot connect to marketplace")
```

### Get Marketplace Stats

```python
# Get public statistics
stats = client.get_public_stats()

print(f"Total Services: {stats['services']['total']}")
print(f"Total API Calls: {stats['apiCalls']['total']}")
print(f"Integrations: {stats['integrations']['total']}")
```

## Popular APIs

### Weather Data

```python
result = client.call_weather_api("London")
# Cost: 0.005 USDC
```

### Web Search

```python
result = client.call_search_api("artificial intelligence")
# Cost: 0.005 USDC
```

### Crypto Prices

```python
result = client.call_crypto_api("ETH")
# Cost: 0.005 USDC
```

### AI Image Generation

```python
result = client.call_image_api("a futuristic city at night")
# Cost: 0.05 USDC
```

### Web Scraping

```python
result = client.call_scraper_api("https://example.com")
# Cost: 0.01 USDC
```

## Error Handling

```python
try:
    result = client.call_weather_api("Paris")

    if result.get("success"):
        print(result["data"])
    elif result.get("payment_required"):
        print("Payment needed")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

except Exception as e:
    print(f"Exception: {str(e)}")
```

## Configuration

### Custom Base URL

```python
# Use local development server
client = X402Client(base_url="http://localhost:3000")
```

### Custom Timeout

```python
# Increase timeout for slow connections
client = X402Client(timeout=60)  # 60 seconds
```

### Environment Variables (Optional)

For automated payment handling:

```bash
export X402_WALLET_PRIVATE_KEY="your_private_key"
export X402_PAYMENT_ENABLED=true
```

**Warning**: Never commit private keys to git!

## Running Examples

### Standalone Example

```bash
python examples/standalone_usage.py
```

This runs through 8 examples demonstrating all client features.

### Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=x402_bazaar

# Run specific test
pytest tests/test_client.py::TestX402Client::test_discover_services

# Run standalone usage tests
pytest tests/test_standalone_usage.py
```

## Troubleshooting

### "Module not found" Error

```bash
# Make sure package is installed
pip install -e .

# Check installation
pip list | grep x402
```

### "Connection timeout" Error

```bash
# Increase timeout
client = X402Client(timeout=60)
```

### "Invalid transaction" Error

- Wait 10-30 seconds after sending payment for blockchain confirmation
- Verify transaction on BaseScan: https://basescan.org/
- Ensure you used the correct chain (Base, not Ethereum mainnet)
- Check transaction was sent to correct address

### Plugin Not Loading in Auto-GPT

```bash
# Verify plugin directory
ls ~/.config/Auto-GPT/plugins/x402_bazaar/

# Check plugins_config.yaml
cat ~/.config/Auto-GPT/plugins_config.yaml

# Restart Auto-GPT
```

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- See [examples/](examples/) for more usage examples
- Visit [x402 Bazaar](https://x402-bazaar.vercel.app) marketplace

## Support

- **Issues**: https://github.com/x402-bazaar/x402-autogpt-plugin/issues
- **Telegram**: @x402_monitoradmin_bot
- **Email**: support@x402-bazaar.com

## Resources

- **Marketplace**: https://x402-api.onrender.com
- **Dashboard**: https://x402-api.onrender.com/dashboard
- **Frontend**: https://x402-bazaar.vercel.app
- **BaseScan**: https://basescan.org/
- **USDC on Base**: https://basescan.org/token/0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

---

Happy API calling! 🚀
