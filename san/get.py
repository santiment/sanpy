import san.sanbase_graphql
from san.graphql import execute_gql
from san.query import get_gql_query, parse_dataset
from san.transform import transform_query_result

CUSTOM_QUERIES = {
    'ohlcv': 'get_ohlcv',
}


def get(dataset, **kwargs):
    query, slug = parse_dataset(dataset)
    if query in CUSTOM_QUERIES:
        return getattr(san.sanbase_graphql, query)(0, slug, **kwargs)

    gql_query = get_gql_query(0, dataset, **kwargs)
    gql_query = "{\n" + gql_query + "\n}"
    res = execute_gql(gql_query)

    return transform_query_result(0, query, res)
