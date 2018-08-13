import san.sanbase_graphql
from san.graphql import execute_gql
from san.error import SanError
from san.pandas_utils import convert_to_datetime_idx_df


def get(dataset, **kwargs):
    gql_query = get_gql_query(0, dataset, **kwargs)
    gql_query = "{\n" + gql_query + "\n}"
    res = execute_gql(gql_query)
    return convert_to_datetime_idx_df(res["query_0"])


def get_gql_query(idx, dataset, **kwargs):
    query, slug = _parse_dataset(dataset)
    return getattr(
        san.sanbase_graphql,
        query,
        lambda *args, **kwargs: not_found(query)
    )(idx, slug, **kwargs)


def _parse_dataset(dataset):
    left, _separator, right = dataset.partition("/")
    return [left, right]


def not_found(query):
    raise SanError(query + ' not found')
