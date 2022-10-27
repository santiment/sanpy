import san.sanbase_graphql
from san.query_constants import DEPRECATED_QUERIES, CUSTOM_QUERIES, NO_SLUG_QUERIES
from san.sanbase_graphql_helper import QUERY_MAPPING
from san.graphql import execute_gql, get_response_headers
from san.query import get_gql_query, parse_dataset
from san.transform import transform_timeseries_data_query_result
from san.error import SanError


def get(dataset, **kwargs):
    """
    The old way of using the `get` funtion is to provide the metric and slug
    as a single string. This requires string interpolation.
    
    Example: 
    
    san.get(
        "daily_active_addresses/bitcoin"
        from_date="2020-01-01"
        to_date="2020-01-10")
    
    The new and preferred way is to provide the slug as a separate parameter.
    
    This allows more flexible selectors to be used instead of a single strings.
    Examples:

    san.get(
        "daily_active_addresses",
        slug="bitcoin",
        from_date="2020-01-01"
        to_date="2020-01-10")

    san.get(
        "dev_activity",
        selector={"organization": "ethereum"},
        from_date="utc_now-60d",
        to_date="utc_now-40d")
    """
    query, slug = parse_dataset(dataset)
    if slug or query in NO_SLUG_QUERIES:
        return __get_metric_slug_string_selector(query, slug, dataset, **kwargs)
    elif query and not slug:
        return __get(query, **kwargs)

def __get_metric_slug_string_selector(query, slug, dataset, **kwargs):
    idx = kwargs.pop('idx', 0)

    if query in DEPRECATED_QUERIES:
        print(
            '**NOTICE**\n{} will be deprecated in version 0.9.0, please use {} instead'.format(
                query, DEPRECATED_QUERIES[query]))
    if query in CUSTOM_QUERIES:
        return getattr(san.sanbase_graphql, query)(idx, slug, **kwargs)
    if query in QUERY_MAPPING.keys():
        gql_query = '{' + get_gql_query(idx, dataset, **kwargs) + '}'
    else:
        if slug != '':
            gql_query = '{' + \
                san.sanbase_graphql.get_metric_timeseries_data(idx, query, slug, **kwargs) + '}'
        else:
            raise SanError('Invalid metric!')
    res = execute_gql(gql_query)

    return transform_timeseries_data_query_result(idx, query, res)


def __get(query, **kwargs):
    if not ('selector' in kwargs or 'slug' in kwargs):
        raise SanError('''
            Invalid call of the get function,you need to either
            give <metric>/<slug> as a first argument or give a slug
            or selector as a key-word argument!''')
    idx = kwargs.pop('idx', 0)
    
    if query in QUERY_MAPPING.keys():
        gql_query = '{' + get_gql_query(idx, query, **kwargs) + '}'
    else:
        gql_query = '{' + san.sanbase_graphql.get_metric_timeseries_data(idx, query, **kwargs) + '}'

    res = execute_gql(gql_query)

    return transform_timeseries_data_query_result(idx, query, res)
