"""
Sanpy CLI - Command-line interface for Santiment API.

Usage:
    san --help              Show all commands
    san get --help          Show help for get command
    san metrics             List all available metrics
    san get price_usd --slug bitcoin --format json
"""

from typing import Optional
import typer
from typing_extensions import Annotated

import san
from san.cli_config import (
    get_api_key,
    set_api_key,
    clear_api_key,
    get_config_path,
    mask_api_key,
)
from san.cli_formatters import (
    format_dataframe,
    format_list,
    format_dict,
    format_api_calls,
    output,
)
from san.error import SanError

# Main app
app = typer.Typer(
    name="san",
    help="Santiment API CLI - cryptocurrency data at your fingertips.",
    add_completion=False,
)

# Config subcommand group
config_app = typer.Typer(help="Manage API configuration.")
app.add_typer(config_app, name="config")


def _init_api_key(api_key: Optional[str] = None) -> None:
    """Initialize API key from flag, env var, or config file."""
    if api_key:
        san.ApiConfig.api_key = api_key
    elif san.ApiConfig.api_key:
        # Already set from env var during import
        pass
    else:
        # Try config file
        stored_key = get_api_key()
        if stored_key:
            san.ApiConfig.api_key = stored_key


def _handle_error(e: Exception) -> None:
    """Handle errors consistently across commands."""
    if isinstance(e, SanError):
        output(f"Error: {e}", err=True)
    else:
        output(f"Unexpected error: {e}", err=True)
    raise typer.Exit(code=1)


# =============================================================================
# Config Commands
# =============================================================================


@config_app.command("set-key")
def config_set_key(
    api_key: Annotated[str, typer.Argument(help="Your Santiment API key")],
) -> None:
    """Store API key in config file."""
    set_api_key(api_key)
    output(f"API key saved to {get_config_path()}")


@config_app.command("show")
def config_show() -> None:
    """Show current configuration."""
    config_path = get_config_path()
    stored_key = get_api_key()
    env_key = san.ApiConfig.api_key

    output(f"Config file: {config_path}")
    output(f"Stored API key: {mask_api_key(stored_key)}")
    if env_key and env_key != stored_key:
        output(f"Env API key (SANPY_APIKEY): {mask_api_key(env_key)}")


@config_app.command("path")
def config_path() -> None:
    """Show config file path."""
    output(str(get_config_path()))


@config_app.command("clear")
def config_clear() -> None:
    """Remove stored API key."""
    clear_api_key()
    output("API key cleared from config file.")


# =============================================================================
# Discovery Commands
# =============================================================================


@app.command()
def metrics(
    slug: Annotated[
        Optional[str],
        typer.Option(help="Filter metrics available for this asset slug"),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: json, csv, table"),
    ] = "table",
    api_key: Annotated[
        Optional[str],
        typer.Option(envvar="SANPY_APIKEY", help="API key"),
    ] = None,
) -> None:
    """List available metrics."""
    _init_api_key(api_key)
    try:
        if slug:
            result = san.available_metrics_for_slug(slug)
        else:
            result = san.available_metrics()
        output(format_list(result, format))
    except Exception as e:
        _handle_error(e)


@app.command()
def projects(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: json, csv, table"),
    ] = "table",
    api_key: Annotated[
        Optional[str],
        typer.Option(envvar="SANPY_APIKEY", help="API key"),
    ] = None,
) -> None:
    """List all available projects/assets."""
    _init_api_key(api_key)
    try:
        df = san.get("projects/all")
        output(format_dataframe(df, format))
    except Exception as e:
        _handle_error(e)


# =============================================================================
# Data Fetching Commands
# =============================================================================


@app.command()
def get(
    metric: Annotated[str, typer.Argument(help="Metric name (e.g., price_usd, daily_active_addresses)")],
    slug: Annotated[str, typer.Option(help="Asset slug (e.g., bitcoin, ethereum)")],
    from_date: Annotated[
        str,
        typer.Option("--from", help="Start date (ISO format or utc_now-Nd)"),
    ] = "utc_now-30d",
    to_date: Annotated[
        str,
        typer.Option("--to", help="End date (ISO format or utc_now)"),
    ] = "utc_now",
    interval: Annotated[
        str,
        typer.Option(help="Data interval (e.g., 1d, 1h, 1w)"),
    ] = "1d",
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: json, csv, table"),
    ] = "table",
    api_key: Annotated[
        Optional[str],
        typer.Option(envvar="SANPY_APIKEY", help="API key"),
    ] = None,
) -> None:
    """Fetch timeseries data for a single metric/asset pair."""
    _init_api_key(api_key)
    try:
        df = san.get(
            metric,
            slug=slug,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
        )
        output(format_dataframe(df, format))
    except Exception as e:
        _handle_error(e)


@app.command("get-many")
def get_many(
    metric: Annotated[str, typer.Argument(help="Metric name (e.g., price_usd)")],
    slugs: Annotated[str, typer.Option(help="Comma-separated asset slugs (e.g., bitcoin,ethereum,solana)")],
    from_date: Annotated[
        str,
        typer.Option("--from", help="Start date (ISO format or utc_now-Nd)"),
    ] = "utc_now-30d",
    to_date: Annotated[
        str,
        typer.Option("--to", help="End date (ISO format or utc_now)"),
    ] = "utc_now",
    interval: Annotated[
        str,
        typer.Option(help="Data interval (e.g., 1d, 1h, 1w)"),
    ] = "1d",
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: json, csv, table"),
    ] = "table",
    api_key: Annotated[
        Optional[str],
        typer.Option(envvar="SANPY_APIKEY", help="API key"),
    ] = None,
) -> None:
    """Fetch timeseries data for a metric across multiple assets."""
    _init_api_key(api_key)
    try:
        slug_list = [s.strip() for s in slugs.split(",") if s.strip()]
        df = san.get_many(
            metric,
            slugs=slug_list,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
        )
        output(format_dataframe(df, format))
    except Exception as e:
        _handle_error(e)


# =============================================================================
# Rate Limit & Complexity Commands
# =============================================================================


@app.command("rate-limit")
def rate_limit(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: json, csv, table"),
    ] = "table",
    api_key: Annotated[
        Optional[str],
        typer.Option(envvar="SANPY_APIKEY", help="API key"),
    ] = None,
) -> None:
    """Show API rate limit status (calls remaining)."""
    _init_api_key(api_key)
    try:
        remaining = san.api_calls_remaining()
        output(format_dict(remaining, format))
    except Exception as e:
        _handle_error(e)


@app.command("api-calls")
def api_calls(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: json, csv, table"),
    ] = "table",
    api_key: Annotated[
        Optional[str],
        typer.Option(envvar="SANPY_APIKEY", help="API key"),
    ] = None,
) -> None:
    """Show API calls history."""
    _init_api_key(api_key)
    try:
        calls = san.api_calls_made()
        output(format_api_calls(calls, format))
    except Exception as e:
        _handle_error(e)


@app.command()
def complexity(
    metric: Annotated[str, typer.Argument(help="Metric name (e.g., price_usd)")],
    from_date: Annotated[
        str,
        typer.Option("--from", help="Start date (ISO format or utc_now-Nd)"),
    ] = "utc_now-30d",
    to_date: Annotated[
        str,
        typer.Option("--to", help="End date (ISO format or utc_now)"),
    ] = "utc_now",
    interval: Annotated[
        str,
        typer.Option(help="Data interval (e.g., 1d, 1h, 1w)"),
    ] = "1d",
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: json, csv, table"),
    ] = "table",
    api_key: Annotated[
        Optional[str],
        typer.Option(envvar="SANPY_APIKEY", help="API key"),
    ] = None,
) -> None:
    """Check query complexity for a metric."""
    _init_api_key(api_key)
    try:
        result = san.metric_complexity(
            metric,
            from_date=from_date,
            to_date=to_date,
            interval=interval,
        )
        data = {
            "metric": metric,
            "from": from_date,
            "to": to_date,
            "interval": interval,
            "complexity": result,
        }
        output(format_dict(data, format))
    except Exception as e:
        _handle_error(e)


# =============================================================================
# Version callback
# =============================================================================


def version_callback(value: bool) -> None:
    if value:
        output(f"sanpy {san.__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", "-v", callback=version_callback, is_eager=True, help="Show version"),
    ] = None,
) -> None:
    """Santiment API CLI - cryptocurrency data at your fingertips."""
    pass


if __name__ == "__main__":
    app()
