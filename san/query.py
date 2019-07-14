import san.sanbase_graphql
import operator
from san.error import SanError
from functools import reduce
from san.pandas_utils import convert_to_datetime_idx_df

QUERY_PATH_MAP = {
    'news': ['news',]
}


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

def transform_query(idx, query, result):
    if query == 'news':
        temporary_result = result['query_' + str(idx)]
        for column in temporary_result:
            column['description'] = column.pop('description')
            column['sourceName'] = column.pop('sourceName')
            column['url'] = column.pop('url')
        print(temporary_result)
        return convert_to_datetime_idx_df(temporary_result)
    return convert_to_datetime_idx_df(result['query_'+str(idx)])

def not_found(query):
    raise SanError(query + ' not found')
