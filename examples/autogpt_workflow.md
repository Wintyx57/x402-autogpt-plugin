# Auto-GPT Workflow Examples

This document shows how the x402 Bazaar plugin integrates with Auto-GPT for autonomous API usage.

## Installation

First, ensure the plugin is installed and enabled in Auto-GPT:

```bash
# Copy plugin to Auto-GPT plugins directory
cp -r src/x402_bazaar ~/.config/Auto-GPT/plugins/

# Enable in plugins_config.yaml
x402-bazaar:
  enabled: true
```

## Example 1: Weather Research Task

**User Goal**: "Find the current weather in Tokyo, Paris, and New York"

### Auto-GPT Workflow:

```
[Auto-GPT] Analyzing goal: Find weather in multiple cities
[Auto-GPT] Executing command: x402_search query="weather"
[x402 Bazaar] Found 3 weather-related APIs
[Auto-GPT] Selected: Weather API (0.005 USDC)
[Auto-GPT] Executing command: x402_call endpoint="/api/weather" params={"city": "Tokyo"}

[x402 Bazaar] Payment Required!
  Amount: 0.005 USDC
  Address: 0xfb1c478BD5567BdcD39782E0D6D23418bFda2430
  Chain: BASE

[Auto-GPT] Requesting user to send payment...
[User] Sends 0.005 USDC on Base, gets tx hash: 0xabc123...

[Auto-GPT] Retrying with payment...
[x402 Bazaar] API call completed:
  Endpoint: /api/weather
  Cost: 0.005 USDC
  Payment: completed

[Auto-GPT] Success! Tokyo: 15°C, Partly Cloudy
[Auto-GPT] Repeating for Paris and New York...

[Auto-GPT] Results:
  - Tokyo: 15°C, Partly Cloudy
  - Paris: 8°C, Rainy
  - New York: 5°C, Snowy

[Auto-GPT] Goal completed!
```

## Example 2: Crypto Analysis

**User Goal**: "Analyze Bitcoin and Ethereum prices, then search for recent news"

### Auto-GPT Workflow:

```
[Auto-GPT] Goal: Analyze BTC and ETH, find news
[Auto-GPT] Step 1: Get crypto prices
[Auto-GPT] Executing: x402_call endpoint="/api/crypto" params={"symbol": "BTC"}

[x402 Bazaar] Payment required: 0.005 USDC
[User] Pays 0.005 USDC...
[Auto-GPT] BTC: $45,230.50 (+2.3%)

[Auto-GPT] Executing: x402_call endpoint="/api/crypto" params={"symbol": "ETH"}
[x402 Bazaar] Using cached payment for same endpoint
[Auto-GPT] ETH: $2,340.80 (+3.1%)

[Auto-GPT] Step 2: Search for crypto news
[Auto-GPT] Executing: x402_call endpoint="/api/search" params={"q": "bitcoin ethereum"}

[x402 Bazaar] Payment required: 0.005 USDC
[User] Pays 0.005 USDC...
[Auto-GPT] Found 10 news articles

[Auto-GPT] Analysis:
  - BTC up 2.3% at $45,230
  - ETH up 3.1% at $2,340
  - Top news: "Crypto markets rally on positive sentiment"

[Auto-GPT] Goal completed!
```

## Example 3: Content Creation

**User Goal**: "Generate an image of a futuristic city and save the URL"

### Auto-GPT Workflow:

```
[Auto-GPT] Goal: Generate AI image
[Auto-GPT] Searching for image generation APIs...
[Auto-GPT] Executing: x402_search query="image"

[x402 Bazaar] Found 2 image-related APIs:
  - AI Image Generation (0.05 USDC)
  - QR Code Generator (0.01 USDC)

[Auto-GPT] Selected: AI Image Generation
[Auto-GPT] Executing: x402_call endpoint="/api/image" method="POST" params={"prompt": "futuristic city at sunset"}

[x402 Bazaar] Payment required: 0.05 USDC
[User] Pays 0.05 USDC...

[Auto-GPT] Image generated successfully!
[Auto-GPT] URL: https://storage.x402.com/images/abc123.png
[Auto-GPT] Saved to: generated_image.txt

[Auto-GPT] Goal completed!
```

## Example 4: Data Research

**User Goal**: "Find stock price of AAPL and recent news about Apple"

### Auto-GPT Workflow:

```
[Auto-GPT] Goal: Research Apple stock
[Auto-GPT] Step 1: Get stock price
[Auto-GPT] Executing: x402_list

[x402 Bazaar] 70 APIs available:
  ...
  - Stock API (0.005 USDC)
  ...

[Auto-GPT] Executing: x402_call endpoint="/api/stock" params={"symbol": "AAPL"}

[x402 Bazaar] Payment required: 0.005 USDC
[User] Pays...
[Auto-GPT] AAPL: $178.50 (+1.2%)

[Auto-GPT] Step 2: Search for Apple news
[Auto-GPT] Executing: x402_call endpoint="/api/search" params={"q": "Apple AAPL"}

[x402 Bazaar] Payment required: 0.005 USDC
[User] Pays...
[Auto-GPT] Found 15 news articles

[Auto-GPT] Report:
  Stock: AAPL at $178.50 (+1.2%)
  News: "Apple announces new product line"
  Sentiment: Positive

[Auto-GPT] Goal completed!
```

## Example 5: Web Scraping & Analysis

**User Goal**: "Scrape https://example.com and analyze the content"

### Auto-GPT Workflow:

```
[Auto-GPT] Goal: Scrape and analyze website
[Auto-GPT] Searching for scraping tools...
[Auto-GPT] Executing: x402_search query="scrape"

[x402 Bazaar] Found 1 scraping API:
  - URL Scraper (0.01 USDC)

[Auto-GPT] Executing: x402_call endpoint="/api/scrape" params={"url": "https://example.com"}

[x402 Bazaar] Payment required: 0.01 USDC
[User] Pays...

[Auto-GPT] Scraped content:
  - Title: Example Domain
  - Text: 1234 words
  - Links: 5 links found

[Auto-GPT] Analysis:
  - Domain age: Established
  - Content type: Information page
  - Key topics: Web standards, examples

[Auto-GPT] Goal completed!
```

## Plugin Commands in Auto-GPT

### `x402_list`

List all available APIs:

```
> x402_list

[x402 Bazaar] 70 APIs available:

  • Weather API
    Get current weather for any city
    Cost: 0.005 USDC

  • Web Search
    Search the web like Google
    Cost: 0.005 USDC

  • Crypto Price API
    Real-time cryptocurrency prices
    Cost: 0.005 USDC

  ... and 67 more APIs
```

### `x402_search`

Search for specific APIs:

```
> x402_search query="translate"

[x402 Bazaar] Found 2 APIs matching 'translate':

  • AI Translation
    Translate text between 100+ languages
    Cost: 0.01 USDC

  • Language Detection
    Detect language of any text
    Cost: 0.005 USDC
```

### `x402_call`

Call any API:

```
> x402_call endpoint="/api/weather" params={"city": "Paris"}

[x402 Bazaar] Calling GET /api/weather...
[x402 Bazaar] Payment required: 0.005 USDC

Instructions:
1. Send 0.005 USDC on BASE to: 0xfb1c478BD5567BdcD39782E0D6D23418bFda2430
2. Wait for transaction confirmation
3. Call this endpoint again with transaction hash

[User sends payment, gets tx: 0xdef456...]

> x402_call endpoint="/api/weather" params={"city": "Paris"} payment_tx="0xdef456..."

[x402 Bazaar] Success! Response:
{
  "city": "Paris",
  "temperature": 8,
  "conditions": "Rainy",
  "humidity": 85,
  "wind_speed": 12
}
```

### `x402_info`

Get marketplace information:

```
> x402_info

[x402 Bazaar] Marketplace Information:
{
  "name": "x402 Bazaar",
  "status": "online",
  "services": 70,
  "integrations": 5,
  "base_url": "https://x402-api.onrender.com"
}
```

## Advanced Use Cases

### Multi-API Workflow

Combine multiple APIs for complex tasks:

```python
# Auto-GPT autonomous workflow
Goal: "Research Tesla, get stock price, find news, and generate summary image"

1. x402_call /api/stock?symbol=TSLA → $245.30
2. x402_call /api/search?q=Tesla → 10 news articles
3. x402_call /api/image (POST) → Generate infographic
4. Combine results into comprehensive report
```

### Conditional API Calls

Use payment status to make decisions:

```python
# Auto-GPT logic
result = x402_call /api/weather?city=Paris

if result.payment_required:
    # Check budget
    if budget >= result.cost_usdc:
        # Proceed with payment
        make_payment()
    else:
        # Use free alternative
        use_free_weather_source()
```

### Batch Processing

Process multiple requests efficiently:

```python
# Auto-GPT batch workflow
cities = ["Tokyo", "Paris", "New York", "London"]

for city in cities:
    result = x402_call /api/weather?city={city}
    save_result(city, result)
```

## Payment Management

### Budget Tracking

Auto-GPT can track spending:

```
[Auto-GPT] Budget: 0.1 USDC
[Auto-GPT] Spent: 0.025 USDC (5 API calls)
[Auto-GPT] Remaining: 0.075 USDC
```

### Payment History

View payment history:

```
[Auto-GPT] Payment History:
  1. Weather API (Tokyo): 0.005 USDC - tx: 0xabc...
  2. Weather API (Paris): 0.005 USDC - tx: 0xdef...
  3. Crypto API (BTC): 0.005 USDC - tx: 0xghi...
  4. Search API: 0.005 USDC - tx: 0xjkl...
  5. Image API: 0.05 USDC - tx: 0xmno...
```

## Best Practices

### 1. Search Before Calling

Always search for the right API first:

```
❌ BAD: Immediately call random endpoints
✅ GOOD: x402_search query="weather" → find best API → call it
```

### 2. Handle Payment Gracefully

Check for payment requirements:

```python
result = x402_call(...)

if result.payment_required:
    # Show clear instructions
    # Wait for user confirmation
    # Retry with payment proof
```

### 3. Cache Results

Don't call the same API multiple times:

```
❌ BAD: Call weather API 10 times for same city
✅ GOOD: Call once, cache result, reuse
```

### 4. Validate Before Paying

Check API parameters before requesting payment:

```python
# Validate input
if not is_valid_city(city):
    return error("Invalid city name")

# Then call API
result = x402_call /api/weather?city={city}
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all API calls are logged
[DEBUG] Calling GET /api/weather?city=Paris
[DEBUG] Response: 402 Payment Required
[DEBUG] Payment details: {...}
```

### Check Plugin Status

```
> x402_info

[x402 Bazaar] Status: Enabled
[x402 Bazaar] Base URL: https://x402-api.onrender.com
[x402 Bazaar] Connection: OK
```

## Resources

- **Plugin Repository**: https://github.com/x402-bazaar/x402-autogpt-plugin
- **Marketplace**: https://x402-bazaar.vercel.app
- **API Docs**: https://x402-api.onrender.com
- **Support**: @x402_monitoradmin_bot

---

This integration enables Auto-GPT to autonomously discover, evaluate, and use paid APIs while managing payments through the x402 protocol.
