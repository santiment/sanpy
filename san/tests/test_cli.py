"""
Unit tests for sanpy CLI.

These tests mock API responses and test CLI behavior.
"""

import json
import pytest
from unittest.mock import patch
from typer.testing import CliRunner
import pandas as pd

from san.cli import app


runner = CliRunner(mix_stderr=False)


# =============================================================================
# Helper fixtures
# =============================================================================


@pytest.fixture
def mock_api_key():
    """Set up a mock API key for tests."""
    with patch("san.ApiConfig") as mock_config:
        mock_config.api_key = "test_api_key_12345"
        yield mock_config


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for mocking san.get() results."""
    return pd.DataFrame(
        {
            "value": [100.0, 101.0, 102.0],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"], utc=True),
    )


@pytest.fixture
def sample_projects_dataframe():
    """Create a sample DataFrame for mocking projects results."""
    return pd.DataFrame(
        {
            "name": ["Bitcoin", "Ethereum", "Santiment"],
            "slug": ["bitcoin", "ethereum", "santiment"],
            "ticker": ["BTC", "ETH", "SAN"],
        }
    )


# =============================================================================
# Version and Help Tests
# =============================================================================


def test_version():
    """Test --version flag."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "sanpy" in result.stdout


def test_help():
    """Test --help flag."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Santiment API CLI" in result.stdout


def test_get_help():
    """Test get --help."""
    result = runner.invoke(app, ["get", "--help"])
    assert result.exit_code == 0
    assert "metric" in result.stdout.lower()
    assert "slug" in result.stdout.lower()


# =============================================================================
# Config Commands Tests
# =============================================================================


def test_config_path():
    """Test config path command."""
    result = runner.invoke(app, ["config", "path"])
    assert result.exit_code == 0
    assert "sanpy" in result.stdout
    assert "config.json" in result.stdout


def test_config_set_key(tmp_path, monkeypatch):
    """Test setting API key."""
    # Use temp directory for config
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    result = runner.invoke(app, ["config", "set-key", "my_test_key_123"])
    assert result.exit_code == 0
    assert "saved" in result.stdout.lower()


def test_config_show(tmp_path, monkeypatch):
    """Test showing config."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    key = "test_key_abcd1234"
    runner.invoke(app, ["config", "set-key", key])

    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0
    assert key[:4] in result.stdout
    assert key not in result.stdout


def test_config_clear(tmp_path, monkeypatch):
    """Test clearing API key."""
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    # First set a key
    runner.invoke(app, ["config", "set-key", "test_key"])

    # Then clear it
    result = runner.invoke(app, ["config", "clear"])
    assert result.exit_code == 0
    assert "cleared" in result.stdout.lower()


# =============================================================================
# Discovery Commands Tests
# =============================================================================


@patch("san.available_metrics")
def test_metrics(mock_available_metrics):
    """Test metrics command."""
    mock_available_metrics.return_value = ["price_usd", "daily_active_addresses", "nvt"]

    result = runner.invoke(app, ["metrics"])
    assert result.exit_code == 0
    assert "price_usd" in result.stdout
    assert "daily_active_addresses" in result.stdout


@patch("san.available_metrics")
def test_metrics_json_format(mock_available_metrics):
    """Test metrics command with JSON output."""
    mock_available_metrics.return_value = ["price_usd", "nvt"]

    result = runner.invoke(app, ["metrics", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "price_usd" in data
    assert "nvt" in data


@patch("san.available_metrics_for_slug")
def test_metrics_for_slug(mock_metrics_for_slug):
    """Test metrics command with slug filter."""
    mock_metrics_for_slug.return_value = ["price_usd", "daily_active_addresses"]

    result = runner.invoke(app, ["metrics", "--slug", "bitcoin"])
    assert result.exit_code == 0
    mock_metrics_for_slug.assert_called_once_with("bitcoin")


@patch("san.get")
def test_projects(mock_get, sample_projects_dataframe):
    """Test projects command."""
    mock_get.return_value = sample_projects_dataframe

    result = runner.invoke(app, ["projects"])
    assert result.exit_code == 0
    assert "bitcoin" in result.stdout.lower()
    mock_get.assert_called_once_with("projects/all")


@patch("san.get")
def test_projects_json_format(mock_get, sample_projects_dataframe):
    """Test projects command with JSON output."""
    mock_get.return_value = sample_projects_dataframe

    result = runner.invoke(app, ["projects", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert len(data) == 3
    assert data[0]["slug"] == "bitcoin"


# =============================================================================
# Get Command Tests
# =============================================================================


@patch("san.get")
def test_get_basic(mock_get, sample_dataframe):
    """Test basic get command."""
    mock_get.return_value = sample_dataframe

    result = runner.invoke(app, ["get", "price_usd", "--slug", "bitcoin"])
    assert result.exit_code == 0
    mock_get.assert_called_once()
    call_kwargs = mock_get.call_args[1]
    assert call_kwargs["slug"] == "bitcoin"


@patch("san.get")
def test_get_with_dates(mock_get, sample_dataframe):
    """Test get command with custom dates."""
    mock_get.return_value = sample_dataframe

    result = runner.invoke(
        app,
        [
            "get",
            "price_usd",
            "--slug",
            "bitcoin",
            "--from",
            "2024-01-01",
            "--to",
            "2024-01-10",
            "--interval",
            "1d",
        ],
    )
    assert result.exit_code == 0
    call_kwargs = mock_get.call_args[1]
    assert call_kwargs["from_date"] == "2024-01-01"
    assert call_kwargs["to_date"] == "2024-01-10"
    assert call_kwargs["interval"] == "1d"


@patch("san.get")
def test_get_json_format(mock_get, sample_dataframe):
    """Test get command with JSON output."""
    mock_get.return_value = sample_dataframe

    result = runner.invoke(app, ["get", "price_usd", "--slug", "bitcoin", "-f", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert len(data) == 3
    assert "value" in data[0]


@patch("san.get")
def test_get_csv_format(mock_get, sample_dataframe):
    """Test get command with CSV output."""
    mock_get.return_value = sample_dataframe

    result = runner.invoke(app, ["get", "price_usd", "--slug", "bitcoin", "-f", "csv"])
    assert result.exit_code == 0
    assert "value" in result.stdout
    assert "100.0" in result.stdout


@patch("san.get")
def test_get_missing_slug(mock_get):
    """Test get command without required slug."""
    result = runner.invoke(app, ["get", "price_usd"])
    assert result.exit_code != 0  # Should fail


# =============================================================================
# Get-Many Command Tests
# =============================================================================


@patch("san.get_many")
def test_get_many_basic(mock_get_many):
    """Test basic get-many command."""
    mock_df = pd.DataFrame(
        {
            "bitcoin": [100.0, 101.0],
            "ethereum": [50.0, 51.0],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02"], utc=True),
    )
    mock_get_many.return_value = mock_df

    result = runner.invoke(app, ["get-many", "price_usd", "--slugs", "bitcoin,ethereum"])
    assert result.exit_code == 0
    call_kwargs = mock_get_many.call_args[1]
    assert call_kwargs["slugs"] == ["bitcoin", "ethereum"]


@patch("san.get_many")
def test_get_many_json_format(mock_get_many):
    """Test get-many command with JSON output."""
    mock_df = pd.DataFrame(
        {
            "bitcoin": [100.0],
            "ethereum": [50.0],
        },
        index=pd.to_datetime(["2024-01-01"], utc=True),
    )
    mock_get_many.return_value = mock_df

    result = runner.invoke(app, ["get-many", "price_usd", "--slugs", "bitcoin,ethereum", "-f", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert len(data) == 1


# =============================================================================
# Rate Limit Commands Tests
# =============================================================================


@patch("san.api_calls_remaining")
def test_rate_limit(mock_remaining):
    """Test rate-limit command."""
    mock_remaining.return_value = {
        "month_remaining": "9000",
        "hour_remaining": "100",
        "minute_remaining": "10",
    }

    result = runner.invoke(app, ["rate-limit"])
    assert result.exit_code == 0
    assert "9000" in result.stdout


@patch("san.api_calls_remaining")
def test_rate_limit_json(mock_remaining):
    """Test rate-limit command with JSON output."""
    mock_remaining.return_value = {
        "month_remaining": "9000",
        "hour_remaining": "100",
        "minute_remaining": "10",
    }

    result = runner.invoke(app, ["rate-limit", "-f", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["month_remaining"] == "9000"


@patch("san.api_calls_remaining")
def test_rate_limit_csv_has_single_trailing_newline(mock_remaining):
    """Test rate-limit CSV output does not include an extra blank line."""
    mock_remaining.return_value = {
        "month_remaining": "9000",
        "hour_remaining": "100",
        "minute_remaining": "10",
    }

    result = runner.invoke(app, ["rate-limit", "-f", "csv"])
    assert result.exit_code == 0
    assert result.stdout == (
        "key,value\n"
        "month_remaining,9000\n"
        "hour_remaining,100\n"
        "minute_remaining,10\n"
    )


@patch("san.api_calls_made")
def test_api_calls(mock_calls_made):
    """Test api-calls command."""
    mock_calls_made.return_value = [
        ("2024-01-01", 50),
        ("2024-01-02", 75),
    ]

    result = runner.invoke(app, ["api-calls"])
    assert result.exit_code == 0
    assert "50" in result.stdout
    assert "75" in result.stdout


# =============================================================================
# Complexity Command Tests
# =============================================================================


@patch("san.metric_complexity")
def test_complexity(mock_complexity):
    """Test complexity command."""
    mock_complexity.return_value = 1500

    result = runner.invoke(app, ["complexity", "price_usd"])
    assert result.exit_code == 0
    assert "1500" in result.stdout


@patch("san.metric_complexity")
def test_complexity_json(mock_complexity):
    """Test complexity command with JSON output."""
    mock_complexity.return_value = 1500

    result = runner.invoke(app, ["complexity", "price_usd", "-f", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["complexity"] == 1500
    assert data["metric"] == "price_usd"


@patch("san.metric_complexity")
def test_complexity_csv_has_single_trailing_newline(mock_complexity):
    """Test complexity CSV output does not include an extra blank line."""
    mock_complexity.return_value = 1500

    result = runner.invoke(app, ["complexity", "price_usd", "-f", "csv"])
    assert result.exit_code == 0
    assert result.stdout == (
        "key,value\n"
        "metric,price_usd\n"
        "from,utc_now-30d\n"
        "to,utc_now\n"
        "interval,1d\n"
        "complexity,1500\n"
    )


# =============================================================================
# Error Handling Tests
# =============================================================================


@patch("san.get")
def test_error_handling(mock_get):
    """Test that errors are handled gracefully."""
    from san.error import SanError

    mock_get.side_effect = SanError("API Error: Invalid metric")

    result = runner.invoke(app, ["get", "invalid_metric", "--slug", "bitcoin"])
    assert result.exit_code == 1
    assert "error" in result.stderr.lower()


# =============================================================================
# Global Options Tests (--retries, --timeout)
# =============================================================================


@patch("san.get")
def test_retries_option(mock_get, sample_dataframe):
    """Test --retries sets ApiConfig.request_retry_count."""
    import san

    original = san.ApiConfig.request_retry_count
    mock_get.return_value = sample_dataframe

    result = runner.invoke(app, ["--retries", "5", "get", "price_usd", "--slug", "bitcoin"])
    assert result.exit_code == 0
    assert san.ApiConfig.request_retry_count == 5

    san.ApiConfig.request_retry_count = original


@patch("san.get")
def test_retries_zero(mock_get, sample_dataframe):
    """Test --retries 0 disables retries."""
    import san

    original = san.ApiConfig.request_retry_count
    mock_get.return_value = sample_dataframe

    result = runner.invoke(app, ["--retries", "0", "get", "price_usd", "--slug", "bitcoin"])
    assert result.exit_code == 0
    assert san.ApiConfig.request_retry_count == 0

    san.ApiConfig.request_retry_count = original


@patch("san.get")
def test_timeout_option(mock_get, sample_dataframe):
    """Test --timeout sets the read timeout in ApiConfig.request_timeout."""
    import san

    original = san.ApiConfig.request_timeout
    mock_get.return_value = sample_dataframe

    result = runner.invoke(app, ["--timeout", "60", "get", "price_usd", "--slug", "bitcoin"])
    assert result.exit_code == 0
    assert san.ApiConfig.request_timeout == (3.05, 60.0)

    san.ApiConfig.request_timeout = original


@patch("san.get")
def test_retries_and_timeout_combined(mock_get, sample_dataframe):
    """Test --retries and --timeout work together."""
    import san

    original_retries = san.ApiConfig.request_retry_count
    original_timeout = san.ApiConfig.request_timeout
    mock_get.return_value = sample_dataframe

    result = runner.invoke(
        app, ["--retries", "1", "--timeout", "10", "get", "price_usd", "--slug", "bitcoin"]
    )
    assert result.exit_code == 0
    assert san.ApiConfig.request_retry_count == 1
    assert san.ApiConfig.request_timeout == (3.05, 10.0)

    san.ApiConfig.request_retry_count = original_retries
    san.ApiConfig.request_timeout = original_timeout


@patch("san.get")
def test_defaults_without_global_options(mock_get, sample_dataframe):
    """Test that ApiConfig defaults are unchanged when no global options are passed."""
    import san

    original_retries = san.ApiConfig.request_retry_count
    original_timeout = san.ApiConfig.request_timeout
    # Reset to known defaults
    san.ApiConfig.request_retry_count = 3
    san.ApiConfig.request_timeout = (3.05, 30)
    mock_get.return_value = sample_dataframe

    result = runner.invoke(app, ["get", "price_usd", "--slug", "bitcoin"])
    assert result.exit_code == 0
    assert san.ApiConfig.request_retry_count == 3
    assert san.ApiConfig.request_timeout == (3.05, 30)

    san.ApiConfig.request_retry_count = original_retries
    san.ApiConfig.request_timeout = original_timeout


def test_retries_shown_in_help():
    """Test that --retries appears in top-level help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--retries" in result.stdout


def test_timeout_shown_in_help():
    """Test that --timeout appears in top-level help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--timeout" in result.stdout
