import platform
from typing import Any

import httpx

import san
from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST
from san.error import SanError


def execute_gql(gql_query_str: str) -> Any:
    default_user_agent = f"sanpy/{san.__version__} (Python {platform.python_version()})"
    headers = {
        "User-Agent": ApiConfig.user_agent or default_user_agent,
    }
    if ApiConfig.api_key:
        headers["authorization"] = "Apikey {}".format(ApiConfig.api_key)

    try:
        response = httpx.post(SANBASE_GQL_HOST, json={"query": gql_query_str}, headers=headers, timeout=60.0)
    except httpx.RequestError as e:
        raise SanError("Error running query: ({})".format(e))

    if response.status_code == 200:
        return __handle_success_response__(response, gql_query_str)
    else:
        if __result_has_gql_errors__(response):
            error_response = response.json()["errors"]["details"]
        else:
            error_response = ""
        raise SanError(
            "Error running query. Status code: {}.\n {}\n {}".format(response.status_code, error_response, gql_query_str)
        )


async def execute_gql_async(gql_query_str: str) -> Any:
    default_user_agent = f"sanpy/{san.__version__} (Python {platform.python_version()})"
    headers = {
        "User-Agent": ApiConfig.user_agent or default_user_agent,
    }
    if ApiConfig.api_key:
        headers["authorization"] = "Apikey {}".format(ApiConfig.api_key)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SANBASE_GQL_HOST, json={"query": gql_query_str}, headers=headers, timeout=60.0)
    except httpx.RequestError as e:
        raise SanError("Error running query: ({})".format(e))

    if response.status_code == 200:
        return __handle_success_response__(response, gql_query_str)
    else:
        if __result_has_gql_errors__(response):
            error_response = response.json().get("errors", {}).get("details", "")
        else:
            error_response = ""
        raise SanError(
            "Error running query. Status code: {}.\n {}\n {}".format(response.status_code, error_response, gql_query_str)
        )


def get_response_headers(gql_query_str: str) -> httpx.Headers:
    default_user_agent = f"sanpy/{san.__version__} (Python {platform.python_version()})"
    headers = {
        "User-Agent": ApiConfig.user_agent or default_user_agent,
    }
    if ApiConfig.api_key:
        headers["authorization"] = "Apikey {}".format(ApiConfig.api_key)

    try:
        response = httpx.post(SANBASE_GQL_HOST, json={"query": gql_query_str}, headers=headers, timeout=60.0)
    except httpx.RequestError as e:
        raise SanError("Error running query: ({})".format(e))

    if response.status_code == 200:
        return response.headers
    else:
        if __result_has_gql_errors__(response):
            error_response = response.json()["errors"]["details"]
        else:
            error_response = ""
        raise SanError(
            "Error running query. Status code: {}.\n {}\n {}".format(response.status_code, error_response, gql_query_str)
        )


def __handle_success_response__(response: httpx.Response, gql_query_str: str) -> Any:
    if __result_has_gql_errors__(response):
        raise SanError("GraphQL error occured running query {} \n errors: {}".format(gql_query_str, response.json()["errors"]))
    elif __exist_not_empty_result(response):
        return response.json()["data"]
    else:
        raise SanError(
            "Error running query, the results are empty. Status code: {}.\n {}".format(response.status_code, gql_query_str)
        )


def __result_has_gql_errors__(response: httpx.Response) -> bool:
    return "errors" in response.json().keys()


def __exist_not_empty_result(response: httpx.Response) -> bool:
    return "data" in response.json().keys() and len(list(filter(lambda x: x is not None, response.json()["data"].values()))) > 0
