import warnings

from san.api_config import ApiConfig
from san.error import SanAuthError, SanEmptyResultError, SanPartialResultWarning, SanQueryError, SanRateLimitError, SanServerError
from san.transport import RequestsTransport

DEFAULT_TRANSPORT = RequestsTransport()


def execute_gql(gql_query_str):
    response = DEFAULT_TRANSPORT.execute(gql_query_str, headers=__build_headers())

    if response.status_code == 200:
        return __handle_success_response__(response, gql_query_str)
    __raise_response_error__(response, gql_query_str)


def get_response_headers(gql_query_str):
    response = DEFAULT_TRANSPORT.execute(gql_query_str, headers=__build_headers())

    if response.status_code == 200:
        return response.headers
    __raise_response_error__(response, gql_query_str)


def __handle_success_response__(response, gql_query_str):
    response_json = __json_response__(response)
    has_data = __exist_not_empty_result(response_json)
    if __result_has_gql_errors__(response_json):
        errors = response_json["errors"]
        if has_data:
            __warn_partial_success__(gql_query_str, errors)
            return response_json["data"]
        __raise_graphql_error__(gql_query_str, errors)
    if has_data:
        return response_json["data"]
    raise SanEmptyResultError(
        "Error running query, the results are empty. Status code: {}.\n {}".format(response.status_code, gql_query_str)
    )


def __build_headers():
    headers = {}
    if ApiConfig.api_key:
        headers = {"authorization": "Apikey {}".format(ApiConfig.api_key)}
    return headers


def __raise_response_error__(response, gql_query_str):
    response_json = __json_response__(response)
    error_response = __extract_error_details__(response_json)
    message = "Error running query. Status code: {}.\n {}\n {}".format(response.status_code, error_response, gql_query_str)

    if response.status_code in (400, 401, 403) and __is_auth_error__(error_response):
        raise SanAuthError(message)
    if response.status_code == 429 or __is_rate_limit_error__(error_response):
        raise SanRateLimitError(message)
    if response.status_code >= 500:
        raise SanServerError(message)
    raise SanQueryError(message)


def __json_response__(response):
    try:
        return response.json()
    except ValueError as exc:
        raise SanQueryError(f"Invalid JSON response received from API: {exc}") from exc


def __result_has_gql_errors__(response_json):
    return "errors" in response_json.keys()


def __exist_not_empty_result(response_json):
    if "data" not in response_json.keys():
        return False

    data = response_json["data"]
    if isinstance(data, dict):
        return len(list(filter(lambda x: x is not None, data.values()))) > 0

    return data is not None


def __extract_error_details__(response_json):
    errors = response_json.get("errors", "")
    if isinstance(errors, dict) and "details" in errors:
        return errors["details"]
    if isinstance(errors, list):
        return "; ".join(filter(None, map(__format_graphql_error__, errors)))
    return errors


def __is_rate_limit_error__(error_response):
    return "API Rate Limit Reached" in str(error_response)


def __is_auth_error__(error_response):
    auth_markers = ["invalid jwt", "invalid apikey", "apikey", "authorization", "unauthorized", "authentication"]
    error_text = str(error_response).lower()
    return any(marker in error_text for marker in auth_markers)


def __raise_graphql_error__(gql_query_str, errors):
    error_response = __extract_error_details__({"errors": errors})
    message = "GraphQL error occured running query {} \n errors: {}".format(gql_query_str, error_response)

    if __is_rate_limit_error__(error_response):
        raise SanRateLimitError(message)
    if __is_auth_error__(error_response):
        raise SanAuthError(message)
    raise SanQueryError(message)


def __format_graphql_error__(error):
    if not isinstance(error, dict):
        return str(error)

    message = error.get("message", "")
    details = error.get("details")
    path = error.get("path")
    parts = [message] if message else []
    if details is not None:
        parts.append(f"details={details}")
    if path is not None:
        parts.append(f"path={path}")
    return " | ".join(parts)


def __warn_partial_success__(gql_query_str, errors):
    error_response = __extract_error_details__({"errors": errors})
    warnings.warn(
        "GraphQL partial success running query {} \n errors: {}".format(gql_query_str, error_response),
        SanPartialResultWarning,
        stacklevel=2,
    )
