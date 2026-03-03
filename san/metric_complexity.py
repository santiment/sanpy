import datetime
from typing import Any

from san.graphql import execute_gql
from san.sanbase_graphql_helper import _format_from_date, _format_to_date
from san.sanitize import sanitize_gql_string


def metric_complexity(metric: str, from_date: str | datetime.datetime, to_date: str | datetime.datetime, interval: str) -> Any:
    metric = sanitize_gql_string(metric)
    interval = sanitize_gql_string(interval)
    query_str = (
        """{{
    getMetric (metric: \"{metric}\") {{
        timeseriesDataComplexity(
            from: \"{from_date}\",
            to: \"{to_date}\",
            interval: \"{interval}\"
        )
        }}
    }}
    """
    ).format(metric=metric, from_date=_format_from_date(from_date), to_date=_format_to_date(to_date), interval=interval)

    return execute_gql(query_str)["getMetric"]["timeseriesDataComplexity"]
