import san.sanbase_graphql
from san.sanbase_graphql_helper import QUERY_MAPPING
from san.graphql import execute_gql
from san.query import get_gql_query, parse_dataset
from san.transform import transform_query_result
from san.error import SanError

CUSTOM_QUERIES = {
    'ohlcv': 'get_ohlcv'
}

DEPRECATED_QUERIES = {
    'mvrv_ratio': 'mvrv_usd',
    'nvt_ratio': 'nvt',
    'realized_value': 'realized_value_usd',
    'token_circulation': 'circulation_1d',
    'burn_rate': 'age_destroyed',
    'token_age_consumed': 'age_destroyed',
    'token_velocity': 'velocity',
    'daily_active_deposits': 'active_deposits',
    'social_volume': 'social_volume_{source}',
    'social_dominance': 'social_dominance_{source}'
}


def get(dataset, **kwargs):
    query, slug = parse_dataset(dataset)
    if query in DEPRECATED_QUERIES:
        print(
            '**NOTICE**\n{} will be deprecated in version 0.9.0, please use {} instead'.format(
                query, DEPRECATED_QUERIES[query]))
    if query in CUSTOM_QUERIES:
        return getattr(san.sanbase_graphql, query)(0, slug, **kwargs)
    if query in QUERY_MAPPING.keys():
        gql_query = "{" + get_gql_query(0, dataset, **kwargs) + "}"
    else:
        if slug != '':
            gql_query = "{" + \
                san.sanbase_graphql.get_metric(0, query, slug, **kwargs) + "}"
        else:
            raise SanError('Invalid metric!')
    res = execute_gql(gql_query)

    return transform_query_result(0, query, res)


def is_rate_limit_exception(exception):
    return 'API Rate Limit Reached' in str(exception)


def rate_limit_time_left(exception):
    words = str(exception).split()
    return int(list(filter(lambda x: x.isnumeric(), words))[0]) # Message is: API Rate Limit Reached. Try again in X seconds (<human readable time>)
