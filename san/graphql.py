from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from san.env_vars import SANBASE_GQL_HOST, SANBASE_GQL_APIKEY


def get_sanbase_gql_client():
    return Client(
            transport=RequestsHTTPTransport(url=SANBASE_GQL_HOST,
                                            headers={'authorization':  "Apikey {}".format(SANBASE_GQL_APIKEY)}),
            fetch_schema_from_transport=True
        )


def execute_gql(gql_query_str):
    query = gql(gql_query_str)
    return get_sanbase_gql_client().execute(query)
