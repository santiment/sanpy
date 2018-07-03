from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from san.api_config import ApiConfig


def get_sanbase_gql_client():
    return Client(
            transport=RequestsHTTPTransport(url=ApiConfig.api_url,
                                            headers={'authorization':  "Apikey {}".format(ApiConfig.api_key)}),
            fetch_schema_from_transport=True
        )


def execute_gql(gql_query_str):
    query = gql(gql_query_str)
    return get_sanbase_gql_client().execute(query)
