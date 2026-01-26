"""
Integration tests for sanpy CLI.

These tests call the real Santiment API and verify CLI behavior.
Run with: pytest -m integration
"""

import json
import re

import pytest
from typer.testing import CliRunner

from san.cli import app


runner = CliRunner()


# =============================================================================
# Discovery Commands Integration Tests
# =============================================================================


@pytest.mark.integration
def test_metrics_integration():
    """Test that metrics command returns real metrics."""
    result = runner.invoke(app, ["metrics"])
    assert result.exit_code == 0
    # These metrics should always exist
    assert "price_usd" in result.stdout


@pytest.mark.integration
def test_metrics_for_slug_integration():
    """Test metrics command with slug filter."""
    result = runner.invoke(app, ["metrics", "--slug", "bitcoin"])
    assert result.exit_code == 0
    assert "price_usd" in result.stdout


@pytest.mark.integration
def test_metrics_json_integration():
    """Test metrics command with JSON output."""
    result = runner.invoke(app, ["metrics", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "price_usd" in data


@pytest.mark.integration
def test_projects_integration():
    """Test that projects command returns real projects."""
    result = runner.invoke(app, ["projects"])
    assert result.exit_code == 0
    assert "bitcoin" in result.stdout.lower()


@pytest.mark.integration
def test_projects_json_integration():
    """Test projects command with JSON output."""
    result = runner.invoke(app, ["projects", "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) > 0
    # Check structure
    slugs = [p["slug"] for p in data]
    assert "bitcoin" in slugs


# =============================================================================
# Get Command Integration Tests
# =============================================================================


@pytest.mark.integration
def test_get_price_integration():
    """Test fetching price data."""
    result = runner.invoke(
        app,
        [
            "get",
            "price_usd",
            "--slug",
            "bitcoin",
            "--from",
            "utc_now-7d",
            "--to",
            "utc_now-2d",
            "--interval",
            "1d",
        ],
    )
    assert result.exit_code == 0
    # Verify column header is present
    assert "value" in result.stdout, "Expected 'value' column header in output"
    # Verify actual numeric data rows exist (decimal values, not just dates)
    # Using regex to match standalone decimal numbers (e.g., "12345.67")
    # This avoids false positives from dates like "2024-01-20"
    assert re.search(r"\b\d+\.\d+\b", result.stdout), "Expected numeric data rows with decimal values"


@pytest.mark.integration
def test_get_json_integration():
    """Test fetching data with JSON output."""
    result = runner.invoke(
        app,
        [
            "get",
            "price_usd",
            "--slug",
            "bitcoin",
            "--from",
            "utc_now-7d",
            "--to",
            "utc_now-2d",
            "--interval",
            "1d",
            "-f",
            "json",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) > 0
    # Check structure - should have datetime and value
    assert "datetime" in data[0] or "value" in data[0]


@pytest.mark.integration
def test_get_csv_integration():
    """Test fetching data with CSV output."""
    result = runner.invoke(
        app,
        [
            "get",
            "price_usd",
            "--slug",
            "bitcoin",
            "--from",
            "utc_now-7d",
            "--to",
            "utc_now-2d",
            "-f",
            "csv",
        ],
    )
    assert result.exit_code == 0
    lines = result.stdout.strip().split("\n")
    assert len(lines) > 1  # Header + data


@pytest.mark.integration
def test_get_daily_active_addresses_integration():
    """Test fetching DAA metric."""
    result = runner.invoke(
        app,
        [
            "get",
            "daily_active_addresses",
            "--slug",
            "bitcoin",
            "--from",
            "utc_now-7d",
            "--to",
            "utc_now-2d",
            "--interval",
            "1d",
        ],
    )
    assert result.exit_code == 0


# =============================================================================
# Get-Many Command Integration Tests
# =============================================================================


@pytest.mark.integration
def test_get_many_integration():
    """Test fetching data for multiple assets."""
    result = runner.invoke(
        app,
        [
            "get-many",
            "price_usd",
            "--slugs",
            "bitcoin,ethereum",
            "--from",
            "utc_now-7d",
            "--to",
            "utc_now-2d",
            "--interval",
            "1d",
        ],
    )
    assert result.exit_code == 0
    # Should have columns for both assets
    assert "bitcoin" in result.stdout.lower() or "ethereum" in result.stdout.lower()


@pytest.mark.integration
def test_get_many_json_integration():
    """Test get-many with JSON output."""
    result = runner.invoke(
        app,
        [
            "get-many",
            "price_usd",
            "--slugs",
            "bitcoin,ethereum",
            "--from",
            "utc_now-7d",
            "--to",
            "utc_now-2d",
            "-f",
            "json",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)


# =============================================================================
# Complexity Command Integration Tests
# =============================================================================


@pytest.mark.integration
def test_complexity_integration():
    """Test complexity calculation."""
    result = runner.invoke(
        app,
        [
            "complexity",
            "price_usd",
            "--from",
            "utc_now-30d",
            "--to",
            "utc_now",
            "--interval",
            "1d",
        ],
    )
    assert result.exit_code == 0
    assert "complexity" in result.stdout.lower()


@pytest.mark.integration
def test_complexity_json_integration():
    """Test complexity with JSON output."""
    result = runner.invoke(
        app,
        [
            "complexity",
            "price_usd",
            "--from",
            "utc_now-30d",
            "--to",
            "utc_now",
            "-f",
            "json",
        ],
    )
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "complexity" in data
    assert "metric" in data
    assert data["metric"] == "price_usd"
    assert isinstance(data["complexity"], int)


# =============================================================================
# Rate Limit Commands Integration Tests (require API key)
# =============================================================================


@pytest.mark.integration
def test_rate_limit_integration():
    """Test rate limit command (requires API key)."""
    result = runner.invoke(app, ["rate-limit"])
    # May fail without API key, but should handle gracefully
    if result.exit_code == 0:
        assert "remaining" in result.stdout.lower() or "month" in result.stdout.lower()
    else:
        # Expected to fail without API key
        assert "error" in result.stdout.lower() or result.exit_code == 1


# =============================================================================
# Error Handling Integration Tests
# =============================================================================


@pytest.mark.integration
def test_invalid_metric_integration():
    """Test handling of invalid metric name."""
    result = runner.invoke(
        app,
        [
            "get",
            "completely_invalid_metric_xyz123",
            "--slug",
            "bitcoin",
            "--from",
            "utc_now-7d",
            "--to",
            "utc_now-2d",
        ],
    )
    # Should fail gracefully
    assert result.exit_code == 1
    assert "error" in result.stdout.lower()


@pytest.mark.integration
def test_invalid_slug_integration():
    """Test handling of invalid slug."""
    result = runner.invoke(
        app,
        [
            "get",
            "price_usd",
            "--slug",
            "completely_invalid_slug_xyz123",
            "--from",
            "utc_now-7d",
            "--to",
            "utc_now-2d",
        ],
    )
    # Should fail gracefully
    assert result.exit_code == 1
