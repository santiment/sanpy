import san.sanbase_graphql
import operator
from san.error import SanError
from functools import reduce
from san.pandas_utils import convert_to_datetime_idx_df
from san.transform import add_transform


def get_gql_query(idx, dataset, **kwargs):
    query, slug = parse_dataset(dataset)
    return getattr(
        san.sanbase_graphql,
        query,
        lambda *args, **kwargs: not_found(query)
    )(idx, slug, **kwargs)


def parse_dataset(dataset):
    left, _separator, right = dataset.partition("/")
    return [left, right]


@add_transform
def transform_query(idx, query, result):
    return convert_to_datetime_idx_df(result)


def not_found(query):
    raise SanError(query + ' not found')
