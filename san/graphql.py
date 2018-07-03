from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST


def get_sanbase_gql_client():
    kwargs = dict(url=SANBASE_GQL_HOST)
    if ApiConfig.api_key:
        kwargs['headers'] = {'authorization':  "Apikey {}".format(ApiConfig.api_key)}

    return Client(
            transport=RequestsHTTPTransport(**kwargs),
            fetch_schema_from_transport=True
        )


def execute_gql(gql_query_str):
    query = gql(gql_query_str)
    return get_sanbase_gql_client().execute(query)
