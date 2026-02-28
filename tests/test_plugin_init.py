"""
Unit tests for x402_bazaar/__init__.py — plugin components.

auto_gpt_plugin_template is not installed, so we mock it to exercise
all branches of X402BazaarPlugin and the register() function.
"""

import json
import sys
import importlib
import pytest
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Fixture: inject a fake auto_gpt_plugin_template module before importing
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="module")
def inject_autogpt_template():
    """Inject a minimal fake auto_gpt_plugin_template so _HAS_AUTOGPT = True."""
    fake_template = MagicMock()
    fake_template.AutoGPTPluginTemplate = object  # plain base class

    sys.modules["auto_gpt_plugin_template"] = fake_template

    # Remove cached version of x402_bazaar so it reimports with the mock
    for key in list(sys.modules.keys()):
        if "x402_bazaar" in key:
            del sys.modules[key]

    import x402_bazaar as pkg
    yield pkg

    # Cleanup
    del sys.modules["auto_gpt_plugin_template"]
    for key in list(sys.modules.keys()):
        if "x402_bazaar" in key:
            del sys.modules[key]


@pytest.fixture
def plugin(inject_autogpt_template):
    """Instantiate X402BazaarPlugin with mocked client."""
    pkg = inject_autogpt_template
    plugin = pkg.X402BazaarPlugin()
    plugin.client = MagicMock()
    return plugin


# ---------------------------------------------------------------------------
# Module-level exports
# ---------------------------------------------------------------------------

class TestModuleExports:
    def test_version_exported(self, inject_autogpt_template):
        pkg = inject_autogpt_template
        assert pkg.__version__ == "0.1.0"

    def test_x402client_exported(self, inject_autogpt_template):
        pkg = inject_autogpt_template
        from x402_bazaar.x402_client import X402Client
        assert pkg.X402Client is X402Client

    def test_plugin_class_exported(self, inject_autogpt_template):
        pkg = inject_autogpt_template
        assert pkg.X402BazaarPlugin is not None

    def test_register_exported(self, inject_autogpt_template):
        pkg = inject_autogpt_template
        assert callable(pkg.register)

    def test_all_contains_plugin(self, inject_autogpt_template):
        pkg = inject_autogpt_template
        assert "X402BazaarPlugin" in pkg.__all__
        assert "register" in pkg.__all__


# ---------------------------------------------------------------------------
# Plugin __init__
# ---------------------------------------------------------------------------

class TestPluginInit:
    def test_name(self, plugin):
        assert plugin._name == "x402-bazaar"

    def test_version(self, plugin):
        assert plugin._version == "0.1.0"

    def test_description_contains_usdc(self, plugin):
        assert "USDC" in plugin._description

    def test_enabled_by_default(self, plugin):
        assert plugin._enabled is True

    def test_command_cache_empty(self, plugin):
        assert plugin._command_cache == {}

    def test_client_created(self, plugin):
        # client is mocked in fixture but it exists
        assert plugin.client is not None


# ---------------------------------------------------------------------------
# can_handle_* methods
# ---------------------------------------------------------------------------

class TestCanHandle:
    def test_can_handle_on_response(self, plugin):
        assert plugin.can_handle_on_response() is True

    def test_can_handle_post_command(self, plugin):
        assert plugin.can_handle_post_command() is True

    def test_can_handle_pre_command(self, plugin):
        assert plugin.can_handle_pre_command() is True

    def test_can_handle_text_embedding(self, plugin):
        assert plugin.can_handle_text_embedding("any text") is False

    def test_can_handle_user_input(self, plugin):
        assert plugin.can_handle_user_input("input") is False

    def test_can_handle_report(self, plugin):
        assert plugin.can_handle_report() is True


# ---------------------------------------------------------------------------
# on_response
# ---------------------------------------------------------------------------

class TestOnResponse:
    def test_returns_response_unchanged_when_disabled(self, plugin):
        plugin._enabled = False
        plugin._command_cache = {"x402_api_call": {"endpoint": "/api/test"}}
        result = plugin.on_response("hello")
        assert result == "hello"

    def test_returns_response_when_cache_empty(self, plugin, capsys):
        plugin._enabled = True
        plugin._command_cache = {}
        result = plugin.on_response("test response")
        assert result == "test response"

    def test_prints_call_info_from_cache(self, plugin, capsys):
        plugin._enabled = True
        plugin._command_cache = {
            "x402_api_call": {
                "endpoint": "/api/weather",
                "cost": "0.01",
                "payment_status": "completed",
            }
        }
        result = plugin.on_response("weather data")
        assert result == "weather data"
        captured = capsys.readouterr()
        assert "/api/weather" in captured.out
        assert "0.01" in captured.out
        assert "completed" in captured.out

    def test_clears_cache_after_response(self, plugin):
        plugin._enabled = True
        plugin._command_cache = {"x402_api_call": {"endpoint": "/api/test"}}
        plugin.on_response("resp")
        assert plugin._command_cache == {}

    def test_no_print_when_no_x402_api_call_key(self, plugin, capsys):
        plugin._enabled = True
        plugin._command_cache = {"other_key": {}}
        plugin.on_response("resp")
        captured = capsys.readouterr()
        assert "API call completed" not in captured.out


# ---------------------------------------------------------------------------
# post_command
# ---------------------------------------------------------------------------

class TestPostCommand:
    def test_returns_response_when_disabled(self, plugin):
        plugin._enabled = False
        result = plugin.post_command("x402 search", "base response")
        assert result == "base response"

    def test_appends_service_count_on_x402_api_command(self, plugin):
        plugin._enabled = True
        plugin.client.discover_services.return_value = [{"name": f"API {i}"} for i in range(5)]
        result = plugin.post_command("x402 search apis", "results")
        assert "5" in result or "APIs available" in result or "x402 Bazaar" in result

    def test_does_not_modify_unrelated_command(self, plugin):
        plugin._enabled = True
        result = plugin.post_command("write_file", "some output")
        assert result == "some output"

    def test_handles_discover_exception_silently(self, plugin):
        plugin._enabled = True
        plugin.client.discover_services.side_effect = Exception("network error")
        # Should not raise
        result = plugin.post_command("x402 list", "output")
        assert result == "output"

    def test_no_append_when_services_empty(self, plugin):
        plugin._enabled = True
        plugin.client.discover_services.return_value = []
        result = plugin.post_command("x402 search", "output")
        # Empty services → no append
        assert result == "output"

    def test_exception_caught_when_search_raises(self, plugin):
        plugin._enabled = True
        plugin.client.discover_services.side_effect = Exception("boom")
        # "x402 search" triggers discover_services; exception must be silently caught
        result = plugin.post_command("x402 search", "output")
        assert result == "output"


# ---------------------------------------------------------------------------
# pre_command
# ---------------------------------------------------------------------------

class TestPreCommand:
    def test_returns_command_unchanged_when_disabled(self, plugin):
        plugin._enabled = False
        result = plugin.pre_command("x402_list", {})
        assert result == "x402_list"

    def test_returns_unrelated_command_unchanged(self, plugin):
        plugin._enabled = True
        result = plugin.pre_command("write_file", {"path": "/tmp/x"})
        assert result == "write_file"

    def test_x402_list_calls_handle_list(self, plugin, capsys):
        plugin._enabled = True
        plugin.client.discover_services.return_value = [
            {"name": "Weather API", "description": "weather", "cost_usdc": "0.01"},
        ]
        result = plugin.pre_command("x402_list", {})
        assert result == "x402_list"
        captured = capsys.readouterr()
        assert "Weather API" in captured.out

    def test_x402_search_calls_handle_search(self, plugin, capsys):
        plugin._enabled = True
        plugin.client.search_services.return_value = [
            {"name": "Crypto API", "description": "crypto prices", "cost_usdc": "0.02"},
        ]
        result = plugin.pre_command("x402_search", {"query": "crypto"})
        assert result == "x402_search"
        captured = capsys.readouterr()
        assert "Crypto API" in captured.out

    def test_x402_call_calls_handle_call_api(self, plugin, capsys):
        plugin._enabled = True
        plugin.client.call_api.return_value = {"success": True, "data": {"temp": 22}}
        result = plugin.pre_command("x402_call", {
            "endpoint": "/api/weather",
            "params": {"city": "Paris"},
            "method": "GET",
        })
        assert result == "x402_call"
        captured = capsys.readouterr()
        assert "/api/weather" in captured.out

    def test_x402_info_calls_handle_marketplace_info(self, plugin, capsys):
        plugin._enabled = True
        plugin.client.get_marketplace_info.return_value = {"name": "x402 Bazaar"}
        result = plugin.pre_command("x402_info", {})
        assert result == "x402_info"
        captured = capsys.readouterr()
        assert "x402 Bazaar" in captured.out


# ---------------------------------------------------------------------------
# handle_text_embedding / user_input
# ---------------------------------------------------------------------------

class TestNotImplemented:
    def test_handle_text_embedding_returns_empty(self, plugin):
        assert plugin.handle_text_embedding("text") == []

    def test_user_input_returns_input_unchanged(self, plugin):
        assert plugin.user_input("hello") == "hello"


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------

class TestReport:
    def test_report_contains_status(self, plugin):
        plugin.client.get_marketplace_info.return_value = {"name": "x402 Bazaar"}
        plugin.client.discover_services.return_value = [
            {"name": "Weather API", "category": "Weather"},
            {"name": "Crypto API", "category": "Crypto"},
        ]
        report = plugin.report()
        assert "Enabled" in report
        assert "0.1.0" in report

    def test_report_contains_api_count(self, plugin):
        plugin.client.get_marketplace_info.return_value = {}
        plugin.client.discover_services.return_value = [{"name": f"API {i}", "category": "X"} for i in range(10)]
        report = plugin.report()
        assert "10" in report

    def test_report_lists_top_categories(self, plugin):
        plugin.client.get_marketplace_info.return_value = {}
        plugin.client.discover_services.return_value = [
            {"name": "A", "category": "Weather"},
            {"name": "B", "category": "Weather"},
            {"name": "C", "category": "Crypto"},
        ]
        report = plugin.report()
        assert "Weather" in report
        assert "2" in report

    def test_report_includes_commands(self, plugin):
        plugin.client.get_marketplace_info.return_value = {}
        plugin.client.discover_services.return_value = []
        report = plugin.report()
        assert "x402_list" in report
        assert "x402_search" in report
        assert "x402_call" in report
        assert "x402_info" in report

    def test_report_returns_error_on_exception(self, plugin):
        plugin.client.get_marketplace_info.side_effect = Exception("network down")
        report = plugin.report()
        assert "Error generating report" in report

    def test_report_disabled_plugin(self, plugin):
        plugin._enabled = False
        plugin.client.get_marketplace_info.return_value = {}
        plugin.client.discover_services.return_value = []
        report = plugin.report()
        assert "Disabled" in report


# ---------------------------------------------------------------------------
# _handle_list_services
# ---------------------------------------------------------------------------

class TestHandleListServices:
    def test_lists_up_to_20_services(self, plugin, capsys):
        services = [{"name": f"API {i}", "description": f"desc {i}", "cost_usdc": "0.01"} for i in range(25)]
        plugin.client.discover_services.return_value = services
        plugin._handle_list_services()
        captured = capsys.readouterr()
        # Should show "and X more" for overflow
        assert "more" in captured.out.lower() or "25" in captured.out

    def test_lists_fewer_than_20_no_overflow(self, plugin, capsys):
        services = [{"name": f"API {i}", "description": "", "cost_usdc": "free"} for i in range(5)]
        plugin.client.discover_services.return_value = services
        plugin._handle_list_services()
        captured = capsys.readouterr()
        assert "more" not in captured.out.lower()

    def test_handles_exception(self, plugin, capsys):
        plugin.client.discover_services.side_effect = Exception("fail")
        plugin._handle_list_services()
        captured = capsys.readouterr()
        assert "Error" in captured.out


# ---------------------------------------------------------------------------
# _handle_search_services
# ---------------------------------------------------------------------------

class TestHandleSearchServices:
    def test_prints_results(self, plugin, capsys):
        plugin.client.search_services.return_value = [
            {"name": "Weather API", "description": "weather", "cost_usdc": "0.01"},
        ]
        plugin._handle_search_services("weather")
        captured = capsys.readouterr()
        assert "Weather API" in captured.out

    def test_handles_exception(self, plugin, capsys):
        plugin.client.search_services.side_effect = Exception("oops")
        plugin._handle_search_services("test")
        captured = capsys.readouterr()
        assert "Error" in captured.out


# ---------------------------------------------------------------------------
# _handle_call_api
# ---------------------------------------------------------------------------

class TestHandleCallApi:
    def test_prints_success(self, plugin, capsys):
        plugin.client.call_api.return_value = {
            "success": True,
            "data": {"temperature": 20},
            "cost_usdc": "0.01",
            "payment_status": "completed",
        }
        plugin._handle_call_api("/api/weather", {"city": "Paris"}, "GET")
        captured = capsys.readouterr()
        assert "Success" in captured.out

    def test_prints_error_on_failure(self, plugin, capsys):
        plugin.client.call_api.return_value = {
            "success": False,
            "error": "Payment required",
        }
        plugin._handle_call_api("/api/weather")
        captured = capsys.readouterr()
        assert "Error" in captured.out or "Payment" in captured.out

    def test_stores_call_info_in_cache(self, plugin):
        plugin.client.call_api.return_value = {
            "success": True,
            "data": {},
            "cost_usdc": "0.02",
            "payment_status": "free",
        }
        plugin._handle_call_api("/api/test")
        assert plugin._command_cache.get("x402_api_call") is not None
        assert plugin._command_cache["x402_api_call"]["endpoint"] == "/api/test"

    def test_handles_exception(self, plugin, capsys):
        plugin.client.call_api.side_effect = Exception("network error")
        plugin._handle_call_api("/api/test")
        captured = capsys.readouterr()
        assert "Error" in captured.out


# ---------------------------------------------------------------------------
# _handle_marketplace_info
# ---------------------------------------------------------------------------

class TestHandleMarketplaceInfo:
    def test_prints_marketplace_info(self, plugin, capsys):
        plugin.client.get_marketplace_info.return_value = {"name": "x402 Bazaar", "version": "1.0"}
        plugin._handle_marketplace_info()
        captured = capsys.readouterr()
        assert "x402 Bazaar" in captured.out

    def test_handles_exception(self, plugin, capsys):
        plugin.client.get_marketplace_info.side_effect = Exception("down")
        plugin._handle_marketplace_info()
        captured = capsys.readouterr()
        assert "Error" in captured.out


# ---------------------------------------------------------------------------
# register()
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_returns_plugin_instance(self, inject_autogpt_template):
        pkg = inject_autogpt_template
        instance = pkg.register()
        assert isinstance(instance, pkg.X402BazaarPlugin)


# ---------------------------------------------------------------------------
# Tests: module loaded WITHOUT auto_gpt_plugin_template (covers lines 23-25, 257-258)
# ---------------------------------------------------------------------------

class TestModuleWithoutAutoGPT:
    """Reload x402_bazaar with auto_gpt_plugin_template blocked to hit the ImportError path."""

    def _fresh_import_without_autogpt(self):
        """
        Reload x402_bazaar with auto_gpt_plugin_template blocked.
        Returns (pkg, saved_x402_modules).
        """
        # Save existing x402_bazaar modules so we can restore later
        saved = {k: v for k, v in sys.modules.items() if "x402_bazaar" in k}
        # Remove them so the next import is fresh
        for key in saved:
            del sys.modules[key]
        # Block auto_gpt_plugin_template by setting it to None in sys.modules
        # (Python raises ImportError when a module entry is None)
        with patch.dict(sys.modules, {"auto_gpt_plugin_template": None}):
            import x402_bazaar as pkg_no_autogpt
            # Capture module reference before context exits
            result = pkg_no_autogpt
        # Remove the no-autogpt version and restore originals
        for key in list(sys.modules.keys()):
            if "x402_bazaar" in key:
                del sys.modules[key]
        sys.modules.update(saved)
        return result

    def test_has_autogpt_false(self):
        pkg = self._fresh_import_without_autogpt()
        assert pkg._HAS_AUTOGPT is False

    def test_plugin_is_none(self):
        pkg = self._fresh_import_without_autogpt()
        assert pkg.X402BazaarPlugin is None

    def test_register_is_none(self):
        pkg = self._fresh_import_without_autogpt()
        assert pkg.register is None

    def test_x402_client_always_importable(self):
        pkg = self._fresh_import_without_autogpt()
        from x402_bazaar.x402_client import X402Client
        # X402Client should always be exported regardless of autogpt availability
        assert pkg.X402Client.__name__ == X402Client.__name__
