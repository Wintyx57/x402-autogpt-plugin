# x402 Bazaar Auto-GPT Plugin

A production-ready Auto-GPT plugin that enables autonomous agents to discover, call, and pay for APIs on the [x402 Bazaar](https://x402-api.onrender.com) marketplace using USDC payments on Base chain.

## Features

- **70+ Premium APIs**: Access weather, web search, crypto prices, AI image generation, web scraping, translations, stock data, and more
- **Automatic x402 Payment Protocol**: Handles payment flow transparently (402 → pay → retry with tx hash)
- **Service Discovery**: Search and discover APIs dynamically
- **Zero Mock Data**: Real production integration with live marketplace
- **Comprehensive Logging**: Track all API calls and payments
- **Auto-GPT Native**: Follows Auto-GPT plugin standard

## Installation

### Prerequisites

- Python 3.8+
- Auto-GPT installed
- USDC wallet on Base chain (for paid API calls)

### Install from Source

```bash
cd x402-autogpt-plugin
pip install -e .
```

### Install from PyPI (coming soon)

```bash
pip install x402-autogpt-plugin
```

## Configuration

### 1. Add Plugin to Auto-GPT

Copy the plugin to your Auto-GPT plugins directory:

```bash
cp -r src/x402_bazaar ~/.config/Auto-GPT/plugins/
```

Or add to `plugins_config.yaml`:

```yaml
x402-bazaar:
  enabled: true
```

### 2. Set Environment Variables (Optional)

For automated payment handling, you can set these environment variables:

```bash
export X402_WALLET_PRIVATE_KEY="your_private_key"  # For automatic payments
export X402_PAYMENT_ENABLED=true                    # Enable auto-payment
```

**Security Warning**: Never commit private keys. Use environment variables or secure key management.

## Usage

### Commands

The plugin registers these commands with Auto-GPT:

#### `x402_list` - List All APIs

```python
x402_list()
```

Lists all 70+ available APIs on x402 Bazaar with names, descriptions, and costs.

#### `x402_search` - Search APIs

```python
x402_search(query="weather")
```

Search for APIs by keyword (e.g., "weather", "crypto", "image").

#### `x402_call` - Call an API

```python
x402_call(
    endpoint="/api/weather",
    params={"city": "Paris"},
    method="GET"
)
```

Call any API endpoint. If payment is required, the plugin will:
1. Receive HTTP 402 with payment details
2. Display payment instructions (amount, address, chain)
3. Wait for user to send USDC
4. Retry with transaction hash

#### `x402_info` - Marketplace Info

```python
x402_info()
```

Get information about the x402 Bazaar marketplace.

### Python Usage (Standalone)

You can also use the client directly without Auto-GPT:

```python
from x402_bazaar import X402Client

# Initialize client
client = X402Client()

# Discover services
services = client.discover_services()
print(f"Found {len(services)} APIs")

# Search for weather APIs
results = client.search_services("weather")

# Call Weather API (no payment)
response = client.call_weather_api("Paris")

if response.get("payment_required"):
    # Payment needed
    details = response["payment_details"]
    print(f"Send {details['payment_amount']} USDC to {details['payment_address']}")

    # After sending payment, retry with tx hash
    tx_hash = "0x123..."  # Your transaction hash
    response = client.call_weather_api("Paris", payment_tx_hash=tx_hash)

# Success!
if response.get("success"):
    print(response["data"])
```

## Available APIs

The x402 Bazaar marketplace offers 70+ APIs across multiple categories:

### Free APIs
- Service Discovery (`/api/services`)
- Search (`/search?q=keyword`)

### Paid APIs (0.005 - 0.05 USDC)

**Data & Information** (0.005 USDC each)
- Weather API - Current weather for any city
- Web Search - Google-like search results
- Crypto Prices - Real-time cryptocurrency data
- Stock Prices - Live stock market data
- News API - Latest news articles
- Exchange Rates - Currency conversion

**AI & Generation** (0.02 - 0.05 USDC each)
- AI Image Generation - Create images from text prompts
- AI Text Generation - GPT-powered text generation
- AI Translation - Multi-language translation
- Sentiment Analysis - Text sentiment detection

**Web Tools** (0.01 - 0.02 USDC each)
- URL Scraper - Extract content from any webpage
- Screenshot API - Capture website screenshots
- PDF Generator - HTML to PDF conversion
- QR Code Generator - Create QR codes

**And 40+ more APIs** for blockchain, social media, databases, analytics, and more.

See full list at: https://x402-api.onrender.com

## Payment Protocol (x402)

The plugin implements the x402 payment protocol:

### Flow

1. **Initial Request**: Call API endpoint without payment
2. **402 Response**: Server returns HTTP 402 Payment Required with:
   ```json
   {
     "amount": "0.005",
     "address": "0xfb1c478BD5567BdcD39782E0D6D23418bFda2430",
     "chain": "base",
     "token": "USDC"
   }
   ```
3. **Payment**: Send USDC on Base to the address
4. **Retry**: Call endpoint again with headers:
   ```
   X-Payment-TxHash: 0x123...
   X-Payment-Chain: base
   ```
5. **Success**: Server verifies payment and returns data (200 OK)

### Payment Details

- **Token**: USDC (USD Coin)
- **Chain**: Base (Coinbase L2)
- **Address**: `0xfb1c478BD5567BdcD39782E0D6D23418bFda2430`
- **Contract**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

## Examples

### Example 1: Get Weather for Paris

```python
from x402_bazaar import X402Client

client = X402Client()

# First call - will require payment
result = client.call_weather_api("Paris")

if result.get("payment_required"):
    print(f"Please send {result['cost_usdc']} USDC")
    print(f"Address: {result['payment_details']['payment_address']}")
    print(f"Chain: {result['payment_details']['payment_chain']}")

    # User sends payment...
    tx_hash = input("Enter transaction hash: ")

    # Retry with payment
    result = client.call_weather_api("Paris", payment_tx_hash=tx_hash)

# Print weather data
if result.get("success"):
    weather = result["data"]
    print(f"Temperature: {weather['temperature']}°C")
    print(f"Conditions: {weather['conditions']}")
```

### Example 2: Search and Call APIs

```python
from x402_bazaar import X402Client

client = X402Client()

# Search for crypto APIs
apis = client.search_services("crypto")

for api in apis:
    print(f"{api['name']}: {api['description']}")
    print(f"Cost: {api['cost_usdc']} USDC")
    print(f"Endpoint: {api['endpoint']}")
    print()

# Call Crypto Price API
result = client.call_crypto_api("BTC")

if result.get("payment_required"):
    print("Payment needed!")
    # Handle payment...
```

### Example 3: Generate AI Image

```python
from x402_bazaar import X402Client

client = X402Client()

# Generate image
prompt = "A futuristic city with flying cars at sunset"
result = client.call_image_api(prompt)

if result.get("payment_required"):
    print(f"Cost: {result['cost_usdc']} USDC")
    # Handle payment...

if result.get("success"):
    image_url = result["data"]["url"]
    print(f"Image generated: {image_url}")
```

## Auto-GPT Integration

Once installed, the plugin automatically integrates with Auto-GPT:

### Goal-Based Usage

Give Auto-GPT goals that require API data:

```
Goal: Find the current weather in Tokyo and the price of Bitcoin

Auto-GPT will:
1. Use x402_list to discover available APIs
2. Use x402_search to find weather and crypto APIs
3. Use x402_call to fetch data (handling payments automatically)
4. Present results to you
```

### Interactive Commands

```bash
# In Auto-GPT CLI
> x402 list
# Shows all 70+ APIs

> x402 search weather
# Shows weather-related APIs

> x402 call /api/weather?city=Paris
# Calls Weather API with payment handling
```

## Architecture

```
x402-autogpt-plugin/
├── src/
│   └── x402_bazaar/
│       ├── __init__.py           # Plugin class (AutoGPTPluginTemplate)
│       │                         # - Command handlers (list, search, call, info)
│       │                         # - Response processing & logging
│       │                         # - Report generation
│       │
│       └── x402_client.py        # HTTP client & payment protocol
│                                 # - discover_services()
│                                 # - search_services()
│                                 # - call_api() with 402 handling
│                                 # - Convenience methods (weather, search, etc.)
│
├── pyproject.toml                # Package metadata
├── setup.py                      # pip installation
├── README.md                     # This file
└── LICENSE                       # MIT License
```

## Development

### Run Tests

```bash
# Unit tests
pytest tests/test_client.py

# Integration tests (requires internet)
pytest tests/test_integration.py

# All tests
pytest
```

### Linting

```bash
flake8 src/
black src/
mypy src/
```

## Troubleshooting

### "Plugin not found" Error

Make sure the plugin is in Auto-GPT's plugins directory:
```bash
ls ~/.config/Auto-GPT/plugins/x402_bazaar/
```

### "Connection timeout" Error

The marketplace may be slow to respond. Increase timeout:
```python
client = X402Client(timeout=60)  # 60 seconds
```

### "Payment verification failed" Error

Wait a few seconds after sending payment for blockchain confirmation:
```python
import time
time.sleep(10)  # Wait 10 seconds
result = client.call_api(..., payment_tx_hash=tx_hash)
```

### "Invalid transaction hash" Error

Make sure you're using the correct transaction hash from Base chain explorer:
- Check on: https://basescan.org/

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## Security

### Private Keys

**NEVER** commit private keys to git. Use environment variables or secure key management:

```bash
# Good
export X402_WALLET_PRIVATE_KEY="your_key"

# Bad
private_key = "your_key"  # DON'T DO THIS
```

### Rate Limiting

The marketplace has rate limits. Use responsibly:
- Max 100 requests/minute per IP
- Paid endpoints have higher limits

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **Website**: https://x402bazaar.org
- **API**: https://x402-api.onrender.com
- **CLI**: https://www.npmjs.com/package/x402-bazaar
- **GitHub Backend**: https://github.com/Wintyx57/x402-backend
- **GitHub Frontend**: https://github.com/Wintyx57/x402-frontend

## Support

- **Issues**: https://github.com/Wintyx57/x402-autogpt-plugin/issues
- **Telegram**: @x402_monitoradmin_bot

## Changelog

### v0.1.0 (2026-02-13)
- Initial release
- 70+ API integrations
- x402 payment protocol support
- Auto-GPT plugin implementation
- Service discovery and search
- Comprehensive logging and reporting
- Production-ready code (zero mocks)

---

Built with ❤️ for the autonomous agent economy
