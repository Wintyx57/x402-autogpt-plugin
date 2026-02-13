# Changelog

All notable changes to the x402 Bazaar Auto-GPT Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Batch API call support
- Automatic payment with wallet integration
- Caching layer for service discovery
- Rate limit handling improvements
- Webhook support for payment notifications

## [0.1.0] - 2026-02-13

### Added
- Initial release of x402 Bazaar Auto-GPT Plugin
- Auto-GPT plugin implementation following AutoGPTPluginTemplate
- X402Client for HTTP requests and payment protocol
- Service discovery: `discover_services()` method
- Service search: `search_services(query)` method
- Generic API calling: `call_api(endpoint, params, method)` method
- x402 payment protocol support (402 → pay → retry with tx hash)
- Convenience methods for popular APIs:
  - `call_weather_api(city)` - Weather data
  - `call_search_api(query)` - Web search
  - `call_crypto_api(symbol)` - Crypto prices
  - `call_image_api(prompt)` - AI image generation
  - `call_scraper_api(url)` - Web scraping
- Marketplace information: `get_marketplace_info()` method
- Public statistics: `get_public_stats()` method
- Service details lookup: `get_service_details(name)` method
- Connection testing: `test_connection()` method
- Auto-GPT commands:
  - `x402_list` - List all APIs
  - `x402_search` - Search APIs
  - `x402_call` - Call any API
  - `x402_info` - Marketplace info
- Plugin lifecycle hooks:
  - `can_handle_pre_command()` / `pre_command()` - Pre-processing
  - `can_handle_post_command()` / `post_command()` - Post-processing
  - `can_handle_on_response()` / `on_response()` - Response logging
  - `can_handle_report()` / `report()` - Usage reporting
- Comprehensive logging with Python logging module
- Error handling for timeouts, network errors, invalid responses
- Payment flow instructions for users
- 70+ API integrations through x402 Bazaar marketplace
- Complete test suite (30+ tests)
- Standalone usage examples
- Full documentation in README.md
- Contributing guidelines
- MIT License

### Development
- Package configuration: `pyproject.toml`, `setup.py`
- Development dependencies: pytest, black, flake8, mypy
- Type hints throughout codebase
- PEP 8 compliant code style
- Automated testing with pytest
- Code coverage reporting
- Example scripts in `examples/`

### Documentation
- Comprehensive README with installation and usage
- API reference in docstrings
- Contributing guidelines
- Code of conduct
- Examples for common use cases
- Troubleshooting guide

### Infrastructure
- PyPI package structure
- GitHub repository ready
- CI/CD ready (.gitignore for common files)
- Entry point for Auto-GPT plugin system

## [0.0.1] - 2026-02-12

### Added
- Project structure initialized
- Basic client skeleton

---

## Version History

### Version 0.1.0 - Initial Release (2026-02-13)

**Highlights:**
- Full x402 payment protocol implementation
- 70+ API integrations
- Zero mock data - production ready
- Comprehensive error handling
- Complete documentation

**What's New:**
- Auto-GPT plugin for x402 Bazaar marketplace
- Service discovery and search
- Automatic payment flow handling
- Convenience methods for popular APIs
- Full test coverage

**Known Limitations:**
- No automatic wallet integration (user must send USDC manually)
- No batch API calls
- No caching layer
- No webhook support

**Upgrade Notes:**
- First release - no upgrade path

---

## Legend

- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security fixes

---

[Unreleased]: https://github.com/x402-bazaar/x402-autogpt-plugin/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/x402-bazaar/x402-autogpt-plugin/releases/tag/v0.1.0
[0.0.1]: https://github.com/x402-bazaar/x402-autogpt-plugin/releases/tag/v0.0.1
