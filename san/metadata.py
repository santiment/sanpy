from .graphql import execute_gql


def metadata(metric, arr):
    return _metadata(execute_gql, metric, arr)


def _metadata(execute, metric, arr):
    query_str = (
        """{{
    getMetric (metric: \"{metric}\") {{
        metadata {{
            """
        + " ".join(arr)
        + """
        }}
    }}
    }}
    """
    ).format(metric=metric)

    return execute(query_str)["getMetric"]["metadata"]
