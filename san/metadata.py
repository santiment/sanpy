from typing import Any

from .graphql import execute_gql
from .sanitize import sanitize_gql_string


def metadata(metric: str, arr: list[str]) -> dict[str, Any]:
    metric = sanitize_gql_string(metric)
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

    return execute_gql(query_str)["getMetric"]["metadata"]
