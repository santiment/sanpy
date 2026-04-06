import inspect
import san.sanbase_graphql
from san.graphql import execute_gql


def available_metrics():
    return _available_metrics(execute_gql)


def _available_metrics(execute):
    sanbase_graphql_functions = inspect.getmembers(san.sanbase_graphql, inspect.isfunction)
    all_functions = list(map(lambda x: x[0], sanbase_graphql_functions)) + execute("{query: getAvailableMetrics}")["query"]
    all_functions = list(filter(lambda x: not (str.startswith(x, "get_metric") or str.startswith(x, "_")), all_functions))
    return all_functions


def available_metrics_for_slug(slug):
    return _available_metrics_for_slug(execute_gql, slug)


def _available_metrics_for_slug(execute, slug):
    query_str = (
        """{{
        projectBySlug(slug: \"{slug}\"){{
            availableMetrics
        }}
    }}
    """
    ).format(slug=slug)

    return execute(query_str)["projectBySlug"]["availableMetrics"]


def available_metric_versions(metric):
    return _available_metric_versions(execute_gql, metric)


def _available_metric_versions(execute, metric):
    query_str = (
        """{{
        getMetric(metric: \"{metric}\"){{
            metadata{{
                availableVersions{{ version }}
            }}
        }}
    }}
    """
    ).format(metric=metric)

    result = execute(query_str)
    get_metric = result.get("getMetric") or {}
    metadata = get_metric.get("metadata") or {}
    versions = metadata.get("availableVersions") or []
    return [v["version"] for v in versions]


def available_metric_for_slug_since(metric, slug):
    return _available_metric_for_slug_since(execute_gql, metric, slug)


def _available_metric_for_slug_since(execute, metric, slug):
    query_str = (
        """{{
        getMetric(metric: \"{metric}\"){{
            availableSince(slug: \"{slug}\")
        }}
    }}
    """
    ).format(metric=metric, slug=slug)

    return execute(query_str)["getMetric"]["availableSince"]
