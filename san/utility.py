import san.sanbase_graphql
from san.error import SanAuthError, SanError, SanRateLimitError
from san.graphql import execute_gql, get_response_headers


def is_rate_limit_exception(exception: Exception) -> bool:
    """Return ``True`` if *exception* indicates an API rate limit."""
    return isinstance(exception, SanRateLimitError) or "API Rate Limit Reached" in str(exception)


def rate_limit_time_left(exception: Exception) -> int:
    """Extract seconds remaining until the rate limit resets."""
    words = str(exception).split()
    return int(
        list(filter(lambda x: x.isnumeric(), words))[0]
    )  # Message is: API Rate Limit Reached. Try again in X seconds (<human readable time>)


def api_calls_remaining() -> dict[str, str]:
    """Return remaining API calls for the current key.

    Returns a dict with ``month_remaining``, ``hour_remaining``,
    and ``minute_remaining`` keys. Requires a valid API key.
    """
    gql_query_str = san.sanbase_graphql.get_api_calls_made()
    res = get_response_headers(gql_query_str)
    return __get_headers_remaining(res)


def api_calls_made() -> list[tuple[str, int]]:
    """Return API call history as ``(datetime, count)`` tuples.

    Requires a valid API key.
    """
    gql_query_str = san.sanbase_graphql.get_api_calls_made()
    res = __request_api_call_data(gql_query_str)
    api_calls = __parse_out_calls_data(res)

    return api_calls


def __request_api_call_data(query):
    try:
        res = execute_gql(query)["currentUser"]["apiCallsHistory"]
    except SanError as exc:
        if "the results are empty" in str(exc):
            raise SanAuthError("No API Key detected...") from exc
        raise
    except (KeyError, TypeError) as exc:
        raise SanError(f"Unexpected API response structure: {exc}") from exc

    return res


def __parse_out_calls_data(response):
    try:
        api_calls = list(map(lambda x: (x["datetime"], x["apiCallsCount"]), response))
    except (KeyError, TypeError) as exc:
        raise SanError(f"Error parsing API response: {exc}") from exc

    return api_calls


def __get_headers_remaining(data):
    try:
        return {
            "month_remaining": data["x-ratelimit-remaining-month"],
            "hour_remaining": data["x-ratelimit-remaining-hour"],
            "minute_remaining": data["x-ratelimit-remaining-minute"],
        }
    except KeyError:
        raise SanAuthError("There are no limits for this API Key.")
