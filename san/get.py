import warnings
from typing import Any

import pandas as pd

import san.sanbase_graphql
from san.error import SanValidationError
from san.graphql import execute_gql
from san.query import get_gql_query, parse_dataset
from san.query_constants import CUSTOM_QUERIES, DEPRECATED_QUERIES, NO_SLUG_QUERIES
from san.sanbase_graphql_helper import QUERY_MAPPING
from san.transform import transform_timeseries_data_query_result


def get(dataset: str, **kwargs: Any) -> pd.DataFrame:
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
    raise SanValidationError(f"Invalid dataset: {dataset!r}")


def __get_metric_slug_string_selector(query: str, slug: str, dataset: str, **kwargs: Any) -> pd.DataFrame:
    idx = kwargs.pop("idx", 0)

    if query in DEPRECATED_QUERIES:
        warnings.warn(
            f"{query} will be deprecated in a future version, please use {DEPRECATED_QUERIES[query]} instead",
            DeprecationWarning,
            stacklevel=3,
        )

    if query in CUSTOM_QUERIES:
        return getattr(san.sanbase_graphql, query)(idx, slug, **kwargs)
    if query in QUERY_MAPPING.keys():
        gql_query = "{" + get_gql_query(idx, dataset, **kwargs) + "}"
    else:
        if slug != "":
            gql_query = "{" + san.sanbase_graphql.get_metric_timeseries_data(idx, query, slug, **kwargs) + "}"
        else:
            raise SanValidationError("Invalid metric!")
    res = execute_gql(gql_query)

    return transform_timeseries_data_query_result(idx, query, res)


def __get(query: str, **kwargs: Any) -> pd.DataFrame:
    if not ("selector" in kwargs or "slug" in kwargs):
        raise SanValidationError("""
            Invalid call of the get function,you need to either
            give <metric>/<slug> as a first argument or give a slug
            or selector as a key-word argument!""")
    idx = kwargs.pop("idx", 0)

    if query in QUERY_MAPPING.keys():
        gql_query = "{" + get_gql_query(idx, query, **kwargs) + "}"
    else:
        gql_query = "{" + san.sanbase_graphql.get_metric_timeseries_data(idx, query, **kwargs) + "}"

    res = execute_gql(gql_query)

    return transform_timeseries_data_query_result(idx, query, res)


async def get_async(dataset: str, **kwargs: Any) -> pd.DataFrame:
    """Async version of :func:`get`. Same arguments and return type."""
    query, slug = parse_dataset(dataset)
    if slug or query in NO_SLUG_QUERIES:
        return await __get_metric_slug_string_selector_async(query, slug, dataset, **kwargs)
    elif query and not slug:
        return await __get_async(query, **kwargs)
    raise SanValidationError(f"Invalid dataset: {dataset!r}")


async def __get_metric_slug_string_selector_async(query: str, slug: str, dataset: str, **kwargs: Any) -> pd.DataFrame:
    from san.graphql import execute_gql_async
    idx = kwargs.pop("idx", 0)

    if query in DEPRECATED_QUERIES:
        warnings.warn(
            f"{query} will be deprecated in a future version, please use {DEPRECATED_QUERIES[query]} instead",
            DeprecationWarning,
            stacklevel=3,
        )

    if query in CUSTOM_QUERIES:
        return getattr(san.sanbase_graphql, query)(idx, slug, **kwargs)
    if query in QUERY_MAPPING.keys():
        gql_query = "{" + get_gql_query(idx, dataset, **kwargs) + "}"
    else:
        if slug != "":
            gql_query = "{" + san.sanbase_graphql.get_metric_timeseries_data(idx, query, slug, **kwargs) + "}"
        else:
            raise SanValidationError("Invalid metric!")

    res = await execute_gql_async(gql_query)
    return transform_timeseries_data_query_result(idx, query, res)


async def __get_async(query: str, **kwargs: Any) -> pd.DataFrame:
    from san.graphql import execute_gql_async
    if not ("selector" in kwargs or "slug" in kwargs):
        raise SanValidationError("""
            Invalid call of the get function,you need to either
            give <metric>/<slug> as a first argument or give a slug
            or selector as a key-word argument!""")
    idx = kwargs.pop("idx", 0)

    if query in QUERY_MAPPING.keys():
        gql_query = "{" + get_gql_query(idx, query, **kwargs) + "}"
    else:
        gql_query = "{" + san.sanbase_graphql.get_metric_timeseries_data(idx, query, **kwargs) + "}"

    res = await execute_gql_async(gql_query)
    return transform_timeseries_data_query_result(idx, query, res)
