import inspect
import san.sanbase_graphql
from san.graphql import execute_gql


def available_metrics():
    sanbase_graphql_functions = inspect.getmembers(san.sanbase_graphql, inspect.isfunction)
    all_functions = list(map(lambda x: x[0], sanbase_graphql_functions)) + execute_gql("{query: getAvailableMetrics}")["query"]
    all_functions = list(filter(lambda x: not (str.startswith(x, "get_metric") or str.startswith(x, "_")), all_functions))
    return all_functions


def available_metrics_for_slug(slug):
    query_str = (
        """{{
        projectBySlug(slug: \"{slug}\"){{
            availableMetrics
        }}
    }}
    """
    ).format(slug=slug)

    return execute_gql(query_str)["projectBySlug"]["availableMetrics"]


def available_metric_versions(metric, names=True):
    """
    Return the versions of a metric by name, e.g.
    ['original:v1', 'modern:v1', 'modern_pit:v1']. A version without a name is
    returned as is. Pass the name as the `version` parameter of san.get and
    san.get_many.

    names=False returns the internal version numbers instead, e.g.
    ['1.0', '2.0', '2.1'].
    """
    query_str = (
        """{{
        getMetric(metric: \"{metric}\"){{
            metadata{{
                availableVersions{{ version versionName }}
            }}
        }}
    }}
    """
    ).format(metric=metric)

    result = execute_gql(query_str)
    get_metric = result.get("getMetric") or {}
    metadata = get_metric.get("metadata") or {}
    versions = metadata.get("availableVersions") or []
    if names:
        return [v.get("versionName") or v["version"] for v in versions]
    return [v["version"] for v in versions]


def available_metric_for_slug_since(metric, slug):
    query_str = (
        """{{
        getMetric(metric: \"{metric}\"){{
            availableSince(slug: \"{slug}\")
        }}
    }}
    """
    ).format(metric=metric, slug=slug)

    return execute_gql(query_str)["getMetric"]["availableSince"]
