import san.sanbase_graphql
from san.graphql import execute_gql
from san.query import parse_dataset
from san.transform import transform_timeseries_data_per_slug_query_result
from san.error import SanError


def get_many(dataset, **kwargs):
    """
    san.get_many(
        "daily_active_addresses",
        slugs=["bitcoin", "ethereum"]
        from_date="2020-01-01"
        to_date="2020-01-10")
    """
    query, slug = parse_dataset(dataset)
    return __get_many(query, **kwargs)


def __get_many(query, **kwargs):
    if not ("selector" in kwargs or "slugs" in kwargs):
        raise SanError("""
            Invalid call of the get function,you need to either
            give <metric>/<slug> as a first argument or give a slug
            or selector as a key-word argument!""")
    idx = kwargs.pop("idx", 0)

    gql_query = "{" + san.sanbase_graphql.get_metric_timeseries_data_per_slug(idx, query, **kwargs) + "}"
    res = execute_gql(gql_query)

    return transform_timeseries_data_per_slug_query_result(idx, query, res)
