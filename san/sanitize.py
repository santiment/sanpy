"""Input validation and sanitization for GraphQL query parameters.

All user-provided values interpolated into GraphQL query strings must be
sanitized to prevent injection attacks and malformed queries.
"""

import re

from san.error import SanValidationError

# Slug: lowercase alphanumeric, hyphens, underscores, dots, colons, forward slashes
_SLUG_RE = re.compile(r"^[a-zA-Z0-9_\-.:/ ]+$")

# Metric name: alphanumeric, underscores
_METRIC_RE = re.compile(r"^[a-zA-Z0-9_]+$")

# Interval: number + letter code (e.g. "1d", "4h", "30m", "1w")
_INTERVAL_RE = re.compile(r"^[0-9]+[smhdwMy]$")

# Ethereum-style address: 0x followed by hex chars
_ETH_ADDRESS_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")


def sanitize_gql_string(value: str) -> str:
    """Escape characters that could break or inject into a GraphQL double-quoted string.

    Escapes backslashes, double quotes, and newlines so the value is safe
    to embed inside a GraphQL \"...\" literal.
    """
    value = value.replace("\\", "\\\\")
    value = value.replace('"', '\\"')
    value = value.replace("\n", "\\n")
    value = value.replace("\r", "\\r")
    return value


def validate_slug(slug: str) -> str:
    """Validate and sanitize a project slug."""
    if not slug or not isinstance(slug, str):
        raise SanValidationError(f"Invalid slug: must be a non-empty string, got {slug!r}")
    slug = slug.strip()
    if not _SLUG_RE.match(slug):
        raise SanValidationError(f"Invalid slug: {slug!r} contains disallowed characters")
    return sanitize_gql_string(slug)


def validate_metric(metric: str) -> str:
    """Validate a metric name."""
    if not metric or not isinstance(metric, str):
        raise SanValidationError(f"Invalid metric: must be a non-empty string, got {metric!r}")
    metric = metric.strip()
    if not _METRIC_RE.match(metric):
        raise SanValidationError(f"Invalid metric: {metric!r} contains disallowed characters")
    return metric


def validate_interval(interval: str) -> str:
    """Validate an interval string (e.g. '1d', '4h', '30m')."""
    if not isinstance(interval, str):
        raise SanValidationError(f"Invalid interval: must be a string, got {type(interval).__name__}")
    interval = interval.strip()
    if not _INTERVAL_RE.match(interval):
        raise SanValidationError(f"Invalid interval: {interval!r} (expected format like '1d', '4h', '30m')")
    return interval


def validate_address(address: str) -> str:
    """Validate an Ethereum-style address."""
    if not address or not isinstance(address, str):
        raise SanValidationError(f"Invalid address: must be a non-empty string, got {address!r}")
    address = address.strip()
    if not _ETH_ADDRESS_RE.match(address):
        raise SanValidationError(f"Invalid address: {address!r} (expected 0x + 40 hex characters)")
    return address


def validate_positive_int(value: int | str, name: str) -> int:
    """Validate that a value is a positive integer."""
    try:
        int_val = int(value)
    except (TypeError, ValueError):
        raise SanValidationError(f"Invalid {name}: must be a positive integer, got {value!r}")
    if int_val < 0:
        raise SanValidationError(f"Invalid {name}: must be non-negative, got {int_val}")
    return int_val
