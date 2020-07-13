import inspect
import san.sanbase_graphql
from san.graphql import execute_gql

def available_metrics():
    sanbase_graphql_functions = inspect.getmembers(san.sanbase_graphql, inspect.isfunction)
    all_functions =  list(map(lambda x: x[0], sanbase_graphql_functions)) + execute_gql('{query: getAvailableMetrics}')['query']
    all_functions.remove('get_metric')
    return all_functions


def available_metrics_for_slug(slug):
    query_str = ("""{{
        projectBySlug(slug: \"{slug}\"){{
            availableMetrics
        }}
    }}
    """).format(
        slug=slug
    )

    return execute_gql(query_str)['projectBySlug']['availableMetrics']


def available_metric_for_slug_since(metric, slug):
    query_str = ("""{{
        getMetric(metric: \"{metric}\"){{
            availableSince(slug: \"{slug}\")
        }}
    }}
    """).format(
        metric=metric,
        slug=slug
    )

    return execute_gql(query_str)['getMetric']['availableSince']
