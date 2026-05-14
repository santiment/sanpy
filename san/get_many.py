import san.sanbase_graphql
from san.graphql import execute_gql
from san.query import parse_dataset
from san.transform import transform_timeseries_data_per_slug_query_result
from san.error import SanError
from san.param_validation import validate_kwargs


def get_many(dataset, **kwargs):
    """
    san.get_many(
        "daily_active_addresses",
        slugs=["bitcoin", "ethereum"]
        from_date="2020-01-01"
        to_date="2020-01-10")
    """
    return _get_many_with_executor(dataset, execute_gql, "san.get_many", **kwargs)


def _get_many_with_executor(dataset, execute, func_name, **kwargs):
    validate_kwargs(func_name, kwargs)
    query, _ = parse_dataset(dataset)
    if not ("selector" in kwargs or "slugs" in kwargs):
        raise SanError("""
            Invalid call of the get function,you need to either
            give <metric>/<slug> as a first argument or give a slug
            or selector as a key-word argument!""")
    idx = kwargs.pop("idx", 0)

    gql_query = "{" + san.sanbase_graphql.get_metric_timeseries_data_per_slug(idx, query, **kwargs) + "}"
    res = execute(gql_query)

    return transform_timeseries_data_per_slug_query_result(idx, query, res)
