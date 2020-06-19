from san.sanbase_graphql_helper import _format_from_date, _format_to_date
from san.graphql import execute_gql


def metric_complexity(metric, from_datetime, to_datetime, interval):
    query_str = ("""{{
    getMetric (metric: \"{metric}\") {{
        timeseriesDataComplexity(
            from: \"{from_datetime}\",
            to: \"{to_datetime}\",
            interval: \"{interval}\"
        )
        }}
    }}
    """).format(
        metric=metric,
        from_datetime=_format_from_date(from_datetime),
        to_datetime=_format_to_date(to_datetime),
        interval=interval
    )

    return execute_gql(query_str)['getMetric']['timeseriesDataComplexity']
