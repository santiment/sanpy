from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


def get_sanbase_gql_client():
    return Client(
            transport=RequestsHTTPTransport(url="https://api.santiment.net/graphql"),
            fetch_schema_from_transport=True
        )


def execute_gql(gql_query_str):
    query = gql(gql_query_str)
    return get_sanbase_gql_client().execute(query)
