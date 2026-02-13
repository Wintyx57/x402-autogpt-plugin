"""
x402 Bazaar Auto-GPT Plugin

A production-ready Auto-GPT plugin that enables autonomous agents to discover,
call, and pay for APIs on the x402 Bazaar marketplace using USDC payments on Base.
"""

# Export client for standalone usage (always available)
from .x402_client import X402Client

__version__ = "0.1.0"
__all__ = ['X402Client', '__version__']

# Only import plugin components if Auto-GPT is available
try:
    import json
    from typing import Any, Dict, List, Optional, Union
    from auto_gpt_plugin_template import AutoGPTPluginTemplate

    _HAS_AUTOGPT = True
    __all__.extend(['X402BazaarPlugin', 'register'])

except ImportError:
    _HAS_AUTOGPT = False
    AutoGPTPluginTemplate = object  # Dummy base class


# Only define plugin class if Auto-GPT is available
if _HAS_AUTOGPT:

    class X402BazaarPlugin(AutoGPTPluginTemplate):
        """
        x402 Bazaar plugin for Auto-GPT.

        Provides seamless access to 70+ paid APIs through x402 Bazaar marketplace,
        with automatic x402 payment protocol handling.
        """

        def __init__(self):
            super().__init__()
            self._name = "x402-bazaar"
            self._version = __version__
            self._description = (
                "Access 70+ paid APIs via x402 Bazaar marketplace with automatic "
                "USDC payments on Base chain. Services include: web search, weather, "
                "crypto prices, AI image generation, web scraping, translations, "
                "stock data, and more."
            )
            self.client = X402Client()
            self._enabled = True
            self._command_cache: Dict[str, Any] = {}

        def can_handle_on_response(self) -> bool:
            """This plugin can process responses."""
            return True

        def on_response(self, response: str, *args, **kwargs) -> str:
            """
            Called when a command returns a response.
            Logs API usage for transparency.
            """
            if self._enabled and self._command_cache:
                if "x402_api_call" in self._command_cache:
                    call_info = self._command_cache["x402_api_call"]
                    print(f"[x402 Bazaar] API call completed:")
                    print(f"  Endpoint: {call_info.get('endpoint', 'unknown')}")
                    print(f"  Cost: {call_info.get('cost', 'unknown')} USDC")
                    print(f"  Payment: {call_info.get('payment_status', 'unknown')}")
                self._command_cache.clear()
            return response

        def can_handle_post_command(self) -> bool:
            """This plugin can handle post-command processing."""
            return True

        def post_command(self, command: str, response: str) -> str:
            """Called after a command is executed."""
            if not self._enabled:
                return response

            if "x402" in command.lower() or "api" in command.lower():
                try:
                    if "search" in command.lower():
                        services = self.client.discover_services()
                        if services:
                            response += f"\n\n[x402 Bazaar] {len(services)} APIs available. "
                            response += "Use 'x402 list' to see all services."
                except Exception:
                    pass
            return response

        def can_handle_pre_command(self) -> bool:
            """This plugin can handle pre-command processing."""
            return True

        def pre_command(self, command: str, arguments: Dict[str, Any]) -> str:
            """Called before a command is executed."""
            if not self._enabled:
                return command

            if command.startswith("x402_"):
                subcommand = command.replace("x402_", "")

                if subcommand == "list":
                    self._handle_list_services()
                elif subcommand == "search":
                    query = arguments.get("query", "")
                    self._handle_search_services(query)
                elif subcommand == "call":
                    endpoint = arguments.get("endpoint", "")
                    params = arguments.get("params", {})
                    method = arguments.get("method", "GET")
                    self._handle_call_api(endpoint, params, method)
                elif subcommand == "info":
                    self._handle_marketplace_info()

            return command

        def can_handle_text_embedding(self, text: str) -> bool:
            """This plugin does not handle text embedding."""
            return False

        def handle_text_embedding(self, text: str) -> List[float]:
            """Not implemented."""
            return []

        def can_handle_user_input(self, user_input: str) -> bool:
            """This plugin does not directly handle user input."""
            return False

        def user_input(self, user_input: str) -> str:
            """Not implemented."""
            return user_input

        def can_handle_report(self) -> bool:
            """This plugin can generate reports."""
            return True

        def report(self) -> str:
            """Generate a report of x402 Bazaar usage."""
            try:
                info = self.client.get_marketplace_info()
                services = self.client.discover_services()

                report = [
                    "=== x402 Bazaar Plugin Report ===",
                    f"Status: {'Enabled' if self._enabled else 'Disabled'}",
                    f"Version: {self._version}",
                    f"Marketplace: {info.get('name', 'x402 Bazaar')}",
                    f"Available APIs: {len(services)}",
                    f"Base URL: https://x402-api.onrender.com",
                    "",
                    "Top Categories:",
                ]

                categories: Dict[str, int] = {}
                for svc in services:
                    cat = svc.get("category", "Other")
                    categories[cat] = categories.get(cat, 0) + 1

                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
                    report.append(f"  - {cat}: {count} APIs")

                report.append("")
                report.append("Commands:")
                report.append("  - x402_list: List all available APIs")
                report.append("  - x402_search: Search for APIs by keyword")
                report.append("  - x402_call: Call an API endpoint (with automatic payment)")
                report.append("  - x402_info: Get marketplace information")

                return "\n".join(report)

            except Exception as e:
                return f"Error generating report: {str(e)}"

        def _handle_list_services(self) -> None:
            """List all available services on x402 Bazaar."""
            try:
                services = self.client.discover_services()
                print(f"\n[x402 Bazaar] {len(services)} APIs available:\n")

                for svc in services[:20]:
                    name = svc.get("name", "Unknown")
                    desc = svc.get("description", "No description")
                    cost = svc.get("cost_usdc", "Free")
                    print(f"  • {name}")
                    print(f"    {desc}")
                    print(f"    Cost: {cost} USDC\n")

                if len(services) > 20:
                    print(f"  ... and {len(services) - 20} more APIs")

            except Exception as e:
                print(f"[x402 Bazaar] Error listing services: {str(e)}")

        def _handle_search_services(self, query: str) -> None:
            """Search for services by keyword."""
            try:
                results = self.client.search_services(query)
                print(f"\n[x402 Bazaar] Found {len(results)} APIs matching '{query}':\n")

                for svc in results:
                    name = svc.get("name", "Unknown")
                    desc = svc.get("description", "No description")
                    cost = svc.get("cost_usdc", "Free")
                    print(f"  • {name}")
                    print(f"    {desc}")
                    print(f"    Cost: {cost} USDC\n")

            except Exception as e:
                print(f"[x402 Bazaar] Error searching services: {str(e)}")

        def _handle_call_api(
            self,
            endpoint: str,
            params: Optional[Dict[str, Any]] = None,
            method: str = "GET"
        ) -> None:
            """Call an API endpoint through x402 Bazaar."""
            try:
                print(f"[x402 Bazaar] Calling {method} {endpoint}...")

                result = self.client.call_api(endpoint, params, method)

                self._command_cache["x402_api_call"] = {
                    "endpoint": endpoint,
                    "cost": result.get("cost_usdc", "unknown"),
                    "payment_status": result.get("payment_status", "unknown"),
                }

                if result.get("success"):
                    print(f"[x402 Bazaar] Success! Response:")
                    print(json.dumps(result.get("data"), indent=2))
                else:
                    print(f"[x402 Bazaar] Error: {result.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"[x402 Bazaar] Error calling API: {str(e)}")

        def _handle_marketplace_info(self) -> None:
            """Get information about the x402 Bazaar marketplace."""
            try:
                info = self.client.get_marketplace_info()
                print("\n[x402 Bazaar] Marketplace Information:")
                print(json.dumps(info, indent=2))

            except Exception as e:
                print(f"[x402 Bazaar] Error getting marketplace info: {str(e)}")


    def register() -> AutoGPTPluginTemplate:
        """Register the x402 Bazaar plugin with Auto-GPT."""
        return X402BazaarPlugin()

else:
    # Provide None placeholders if Auto-GPT is not available
    X402BazaarPlugin = None
    register = None
