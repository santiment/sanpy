import requests


def execute_gql(gql_query_str):
    from san.client import get_default_client

    return get_default_client().execute_gql(gql_query_str)


def get_response_headers(gql_query_str):
    from san.client import get_default_client

    return get_default_client().get_response_headers(gql_query_str)
