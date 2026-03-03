import datetime
from typing import Any

from san.graphql import execute_gql
from san.sanbase_graphql_helper import _format_from_date, _format_to_date
from san.sanitize import sanitize_gql_string


def metric_complexity(metric: str, from_date: str | datetime.datetime, to_date: str | datetime.datetime, interval: str) -> Any:
    """Return the query complexity score for a metric with the given parameters.

    A single API request may have a maximum complexity of 50000.

    Args:
        metric: Metric name (e.g. ``"price_usd"``).
        from_date: Start of the period (ISO 8601 string or datetime).
        to_date: End of the period (ISO 8601 string or datetime).
        interval: Data point interval (e.g. ``"1d"``, ``"1h"``).
    """
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
