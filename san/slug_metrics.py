from .graphql import execute_gql

def slug_metrics(slug):
    query_str = ("""{{
        projectBySlug(slug: \"{slug}\"){{
            availableMetrics
        }}
    }}
    """).format(
        slug=slug
    )

    return execute_gql(query_str)['projectBySlug']['availableMetrics']
