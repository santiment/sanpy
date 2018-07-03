from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST
from san.error import SanError


def get_sanbase_gql_client():
    if not ApiConfig.api_key:
        raise SanError("Please provide valid api key!")

    return Client(
            transport=RequestsHTTPTransport(url=SANBASE_GQL_HOST,
                                            headers={'authorization':  "Apikey {}".format(ApiConfig.api_key)}),
            fetch_schema_from_transport=True
        )


def execute_gql(gql_query_str):
    query = gql(gql_query_str)
    return get_sanbase_gql_client().execute(query)
