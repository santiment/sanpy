import json
import requests
from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST
from san.error import SanError


def execute_gql(gql_query_str):
    headers = {}
    if ApiConfig.api_key:
        headers = {'authorization': "Apikey {}".format(ApiConfig.api_key)}

    try:
        response = requests.post(
            SANBASE_GQL_HOST,
            json={'query': gql_query_str},
            headers=headers)
    except requests.exceptions.RequestException as e:
        raise SanError('Error running query: ({})'.format(e))

    if response.status_code == 200:
        return __handle_success_response__(response, gql_query_str)
    else:
        if __result_has_gql_errors__(response):
            error_response = response.json()['errors']['details']
        else:
            error_response = ''
        raise SanError(
            "Error running query. Status code: {}.\n {}\n {}".format(
                response.status_code,
                error_response,
                gql_query_str))


def get_response_headers(gql_query_str):
    headers = {}
    if ApiConfig.api_key:
        headers = {'authorization': "Apikey {}".format(ApiConfig.api_key)}

    try:
        response = requests.post(
            SANBASE_GQL_HOST,
            json={'query': gql_query_str},
            headers=headers)
    except requests.exceptions.RequestException as e:
        raise SanError('Error running query: ({})'.format(e))
    
    if response.status_code == 200:
        return response.headers
    else:
        if __result_has_gql_errors__(response):
            error_response = response.json()['errors']['details']
        else:
            error_response = ''
        raise SanError(
            "Error running query. Status code: {}.\n {}\n {}".format(
                response.status_code,
                error_response,
                gql_query_str))


def __handle_success_response__(response, gql_query_str):
    if __result_has_gql_errors__(response):
        raise SanError(
            "GraphQL error occured running query {} \n errors: {}".format(
                gql_query_str,
                response.json()['errors']))
    elif __exist_not_empty_result(response):
        return response.json()['data']
    else:
        raise SanError(
            "Error running query, the results are empty. Status code: {}.\n {}" .format(
                response.status_code,
                gql_query_str))


def __result_has_gql_errors__(response):
    return 'errors' in response.json().keys()


def __exist_not_empty_result(response):
    return 'data' in response.json().keys() and len(
        list(
            filter(
                lambda x: x is not None,
                response.json()['data'].values()))) > 0
