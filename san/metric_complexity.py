from san.sanbase_graphql_helper import _format_from_date, _format_to_date
from san.graphql import execute_gql


def metric_complexity(metric, from_date, to_date, interval):
    query_str = ("""{{
    getMetric (metric: \"{metric}\") {{
        timeseriesDataComplexity(
            from: \"{from_date}\",
            to: \"{to_date}\",
            interval: \"{interval}\"
        )
        }}
    }}
    """).format(
        metric=metric,
        from_date=_format_from_date(from_date),
        to_date=_format_to_date(to_date),
        interval=interval
    )

    return execute_gql(query_str)['getMetric']['timeseriesDataComplexity']
