import requests
from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST
from san.error import SanError


def execute_gql(gql_query_str: str) -> dict:
    """
    Executes a GraphQL query and returns the result as a dictionary.
    :param gql_query_str: The GraphQL query to execute.
    :return: The result of the query as a dictionary.
    """
    response = __execute_gql__(gql_query_str)
    data, headers = __handle_response__(response, gql_query_str)
    return data


def get_response_headers(gql_query_str: str) -> dict:
    """
    Executes a GraphQL query and returns the response headers.
    :param gql_query_str: The GraphQL query to execute.
    :return: The response headers.
    """
    response = __execute_gql__(gql_query_str)
    data, headers = __handle_response__(response, gql_query_str)
    return headers


def __execute_gql__(gql_query_str: str) -> requests.Response:
    """
    Executes a GraphQL query and returns the response.
    :param gql_query_str: The GraphQL query to execute.
    :return: The requests.Response.
    """
    headers = {}
    if ApiConfig.api_key is not None:
        headers = {"authorization": f"Apikey {ApiConfig.api_key}"}
    try:
        response = requests.post(
            SANBASE_GQL_HOST, json={"query": gql_query_str}, headers=headers
        )
        return response
    except requests.exceptions.RequestException as e:
        raise SanError(f"Error running query: ({e})")


def __handle_response__(
    response: requests.Response, gql_query_str: str
) -> (dict, dict):
    """
    Handles the response from the GraphQL query.
    :param response: The response from the GraphQL query.
    :param gql_query_str: The GraphQL query to execute.
    :return: The result of the query as a tuple of dictionaries.
    """
    response_json = response.json()
    response_status_code = response.status_code
    error_response = response_json.get("errors", "")
    if __result_has_gql_errors__(response):
        raise SanError(
            f"GraphQL error occurred running query {gql_query_str} \n errors: {error_response}"
        )
    elif __exist_not_empty_result__(response):
        return response_json["data"], response.headers
    else:
        raise SanError(
            f"Error running query, the results are empty. Status code: {response_status_code}.\n {gql_query_str}"
        )


def __result_has_gql_errors__(response: requests.Response) -> bool:
    """
    Checks if the response from the GraphQL query contains errors key.
    :param response: The response from the GraphQL query.
    :return: True if the response contains errors key, False otherwise.
    """
    return "errors" in response.json().keys()


def __exist_not_empty_result__(response: requests.Response) -> bool:
    """
    Checks if the response from the GraphQL query contains data key and the data is not empty.
    :param response: The response from the GraphQL query.
    :return: True if the response contains data key and the data is not empty, False otherwise.
    """
    return (
        "data" in response.json().keys()
        and len(list(filter(lambda x: x is not None, response.json()["data"].values())))
        > 0
    )
