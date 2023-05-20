import inspect
import san.sanbase_graphql
from san.graphql import execute_gql


def available_metrics() -> list:
    """
    Returns a list of all available metrics
    :param: None
    :return: list of all available metrics
    """
    sanbase_graphql_functions = inspect.getmembers(
        san.sanbase_graphql, inspect.isfunction
    )
    all_functions = (
        list(map(lambda x: x[0], sanbase_graphql_functions))
        + execute_gql("{query: getAvailableMetrics}")["query"]
    )
    all_functions = list(
        filter(
            lambda x: not (str.startswith(x, "get_metric") or str.startswith(x, "_")),
            all_functions,
        )
    )
    return all_functions


def available_metrics_for_slug(slug: str) -> list:
    """
    Returns a list of all available metrics for a given slug
    :param slug: slug of the project
    :return: list of all available metrics for a given slug

    """
    query_str = f"""{{
        projectBySlug(slug: \"{slug}\"){{
            availableMetrics
        }}
    }}
    """
    return execute_gql(query_str)["projectBySlug"]["availableMetrics"]


def available_metric_for_slug_since(metric: str, slug: str) -> str:
    """
    Returns the date since a metric is available for a given slug
    :param metric: metric name
    :param slug: slug of the project
    :return: datetime since a metric is available for a given slug
    """
    query_str = f"""{{
        getMetric(metric: \"{metric}\"){{
            availableSince(slug: \"{slug}\")
        }}
    }}
    """

    return execute_gql(query_str)["getMetric"]["availableSince"]
