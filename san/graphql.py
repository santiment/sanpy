import asyncio
import logging
import platform
import time
from typing import Any, NoReturn

import httpx

import san
from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST
from san.error import SanAuthError, SanQueryError, SanRateLimitError

logger = logging.getLogger("sanpy")

_RATE_LIMIT_MARKER = "API Rate Limit Reached"

# ---------------------------------------------------------------------------
# Lazy-initialized HTTP clients (connection pooling)
# ---------------------------------------------------------------------------

_sync_client: httpx.Client | None = None
_async_client: httpx.AsyncClient | None = None


def _get_sync_client() -> httpx.Client:
    """Return (and lazily create) a module-level httpx.Client for connection reuse."""
    global _sync_client
    if _sync_client is None or _sync_client.is_closed:
        _sync_client = httpx.Client()
    return _sync_client


def _get_async_client() -> httpx.AsyncClient:
    """Return (and lazily create) a module-level httpx.AsyncClient for connection reuse."""
    global _async_client
    if _async_client is None or _async_client.is_closed:
        _async_client = httpx.AsyncClient()
    return _async_client


def close_client() -> None:
    """Close the module-level HTTP clients. Call on shutdown if desired."""
    global _sync_client, _async_client
    if _sync_client is not None and not _sync_client.is_closed:
        _sync_client.close()
        _sync_client = None
    if _async_client is not None and not _async_client.is_closed:
        asyncio.get_event_loop().run_until_complete(_async_client.aclose())
        _async_client = None


# ---------------------------------------------------------------------------
# Headers & error helpers
# ---------------------------------------------------------------------------


def _build_headers() -> dict[str, str]:
    """Build common HTTP headers for GraphQL requests."""
    default_user_agent = f"sanpy/{san.__version__} (Python {platform.python_version()})"
    headers = {
        "User-Agent": ApiConfig.user_agent or default_user_agent,
    }
    if ApiConfig.api_key:
        headers["authorization"] = f"Apikey {ApiConfig.api_key}"
    return headers


def _redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Return a copy of headers with the API key redacted for safe logging."""
    redacted = dict(headers)
    if "authorization" in redacted:
        redacted["authorization"] = "Apikey ***"
    return redacted


def _extract_error_details(response: httpx.Response) -> str:
    """Safely extract error details from a GraphQL error response."""
    if _result_has_gql_errors(response):
        return response.json().get("errors", {}).get("details", "")
    return ""


def _raise_status_error(response: httpx.Response, gql_query_str: str) -> NoReturn:
    """Raise a specific SanError subclass based on the HTTP status code."""
    error_response = _extract_error_details(response)
    msg = f"Error running query. Status code: {response.status_code}.\n {error_response}\n {gql_query_str}"

    if response.status_code == 429 or _RATE_LIMIT_MARKER in error_response:
        raise SanRateLimitError(msg)
    if response.status_code in (401, 403):
        raise SanAuthError(msg)
    raise SanQueryError(msg, status_code=response.status_code)


def _is_retryable(exc: Exception) -> bool:
    """Return True if the exception is worth retrying."""
    if isinstance(exc, (httpx.RequestError, SanRateLimitError)):
        return True
    if isinstance(exc, SanQueryError) and exc.status_code is not None and exc.status_code >= 500:
        return True
    return False


# ---------------------------------------------------------------------------
# Retry wrapper
# ---------------------------------------------------------------------------


def _retry_delay(attempt: int) -> float:
    """Compute exponential backoff delay: base * 2^attempt."""
    return ApiConfig.retry_base_delay * (2**attempt)


def _execute_with_retry(fn: Any, *args: Any, **kwargs: Any) -> Any:
    """Call *fn* with retry + exponential backoff for transient failures."""
    max_retries = ApiConfig.max_retries

    for attempt in range(max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            if not _is_retryable(exc) or attempt >= max_retries:
                raise
            delay = _retry_delay(attempt)
            logger.warning("Retry %d/%d after %.1fs: %s", attempt + 1, max_retries, delay, exc)
            time.sleep(delay)

    raise RuntimeError("unreachable")  # pragma: no cover


async def _execute_with_retry_async(fn: Any, *args: Any, **kwargs: Any) -> Any:
    """Async version of _execute_with_retry."""
    max_retries = ApiConfig.max_retries

    for attempt in range(max_retries + 1):
        try:
            return await fn(*args, **kwargs)
        except Exception as exc:
            if not _is_retryable(exc) or attempt >= max_retries:
                raise
            delay = _retry_delay(attempt)
            logger.warning("Async retry %d/%d after %.1fs: %s", attempt + 1, max_retries, delay, exc)
            await asyncio.sleep(delay)

    raise RuntimeError("unreachable")  # pragma: no cover


# ---------------------------------------------------------------------------
# Core execution functions
# ---------------------------------------------------------------------------


def _execute_gql_once(gql_query_str: str) -> Any:
    """Execute a single GraphQL request (no retry).

    Raises raw ``httpx.RequestError`` on connection failures so the retry
    wrapper can decide whether to retry.
    """
    headers = _build_headers()
    timeout = ApiConfig.request_timeout

    logger.debug("GQL request: %s", gql_query_str[:200])
    logger.debug("Headers: %s", _redact_headers(headers))

    response = _get_sync_client().post(
        SANBASE_GQL_HOST, json={"query": gql_query_str}, headers=headers, timeout=timeout
    )

    logger.debug("Response status: %d", response.status_code)

    if response.status_code == 200:
        return _handle_success_response(response, gql_query_str)
    else:
        _raise_status_error(response, gql_query_str)


def execute_gql(gql_query_str: str) -> Any:
    try:
        return _execute_with_retry(_execute_gql_once, gql_query_str)
    except httpx.RequestError as e:
        logger.error("Request failed: %s", e)
        raise SanQueryError(f"Error running query: ({e})")


async def _execute_gql_async_once(gql_query_str: str) -> Any:
    """Execute a single async GraphQL request (no retry)."""
    headers = _build_headers()
    timeout = ApiConfig.request_timeout

    logger.debug("GQL async request: %s", gql_query_str[:200])

    client = _get_async_client()
    response = await client.post(
        SANBASE_GQL_HOST, json={"query": gql_query_str}, headers=headers, timeout=timeout
    )

    logger.debug("Async response status: %d", response.status_code)

    if response.status_code == 200:
        return _handle_success_response(response, gql_query_str)
    else:
        _raise_status_error(response, gql_query_str)


async def execute_gql_async(gql_query_str: str) -> Any:
    try:
        return await _execute_with_retry_async(_execute_gql_async_once, gql_query_str)
    except httpx.RequestError as e:
        logger.error("Async request failed: %s", e)
        raise SanQueryError(f"Error running query: ({e})")


def get_response_headers(gql_query_str: str) -> httpx.Headers:
    headers = _build_headers()
    timeout = ApiConfig.request_timeout

    try:
        response = _get_sync_client().post(
            SANBASE_GQL_HOST, json={"query": gql_query_str}, headers=headers, timeout=timeout
        )
    except httpx.RequestError as e:
        raise SanQueryError(f"Error running query: ({e})")

    if response.status_code == 200:
        return response.headers
    else:
        _raise_status_error(response, gql_query_str)


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------


def _handle_success_response(response: httpx.Response, gql_query_str: str) -> Any:
    if _result_has_gql_errors(response):
        error_str = str(response.json()["errors"])
        if _RATE_LIMIT_MARKER in error_str:
            raise SanRateLimitError(
                f"GraphQL error running query {gql_query_str} \n errors: {error_str}"
            )
        raise SanQueryError(f"GraphQL error running query {gql_query_str} \n errors: {error_str}")
    elif _exist_not_empty_result(response):
        return response.json()["data"]
    else:
        raise SanQueryError(
            f"Error running query, the results are empty. Status code: {response.status_code}.\n {gql_query_str}"
        )


def _result_has_gql_errors(response: httpx.Response) -> bool:
    return "errors" in response.json()


def _exist_not_empty_result(response: httpx.Response) -> bool:
    data = response.json().get("data")
    return data is not None and any(v is not None for v in data.values())
