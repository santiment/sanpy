from .graphql import execute_gql

def metadata(metric, arr):
    query_str = ("""{{
    getMetric (metric: \"{metric}\") {{
        metadata {{
            """ + ' '.join(arr) + """
        }}
    }}
    }}
    """).format(
        metric=metric
    )

    return execute_gql(query_str)['getMetric']['metadata']
