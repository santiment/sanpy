import inspect

import san.sanbase_graphql
from san.cache import _metadata_cache
from san.graphql import execute_gql
from san.sanitize import sanitize_gql_string


def available_metrics() -> list[str]:
    """Return a list of all available metric names.

    Results are cached for 300 seconds. Use :func:`san.clear_cache` to
    force a fresh fetch.
    """
    cached = _metadata_cache.get("available_metrics")
    if cached is not None:
        return cached

    sanbase_graphql_functions = inspect.getmembers(san.sanbase_graphql, inspect.isfunction)
    all_functions = list(map(lambda x: x[0], sanbase_graphql_functions)) + execute_gql("{query: getAvailableMetrics}")["query"]
    all_functions = list(filter(lambda x: not (str.startswith(x, "get_metric") or str.startswith(x, "_")), all_functions))

    _metadata_cache.set("available_metrics", all_functions)
    return all_functions


def available_metrics_for_slug(slug: str) -> list[str]:
    """Return metrics available for a specific project *slug*.

    Results are cached for 300 seconds per slug.
    """
    cache_key = f"available_metrics_for_slug:{slug}"
    cached = _metadata_cache.get(cache_key)
    if cached is not None:
        return cached

    slug = sanitize_gql_string(slug)
    query_str = (
        """{{
        projectBySlug(slug: \"{slug}\"){{
            availableMetrics
        }}
    }}
    """
    ).format(slug=slug)

    result = execute_gql(query_str)["projectBySlug"]["availableMetrics"]
    _metadata_cache.set(cache_key, result)
    return result


def available_metric_for_slug_since(metric: str, slug: str) -> str | None:
    """Return the earliest datetime a *metric* is available for *slug*.

    Returns an ISO 8601 string or ``None`` if unavailable.
    """
    metric = sanitize_gql_string(metric)
    slug = sanitize_gql_string(slug)
    query_str = (
        """{{
        getMetric(metric: \"{metric}\"){{
            availableSince(slug: \"{slug}\")
        }}
    }}
    """
    ).format(metric=metric, slug=slug)

    return execute_gql(query_str)["getMetric"]["availableSince"]
