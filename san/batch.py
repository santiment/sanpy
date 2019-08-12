import san.sanbase_graphql
from san.query import get_gql_query
from san.graphql import execute_gql
from san.transform import transform_query_result
from san.v2_metrics_list import V2_METRIC_QUERIES

class Batch:

    def __init__(self):
        self.queries = []

    def get(self, dataset, **kwargs):
        self.queries.append([dataset, kwargs])

    def execute(self):
        result = []
        batched_queries = []

        for idx, query in enumerate(self.queries):
            [metric, slug] = query[0].split('/')
            if metric in V2_METRIC_QUERIES:
                batched_queries.append(
                    san.sanbase_graphql.get_metric(
                        idx, metric, slug, **query[1]))
            else:
                batched_queries.append(get_gql_query(idx, query[0], **query[1]))

        gql_string = self.__batch_gql_queries(batched_queries)
        res = execute_gql(gql_string)

        idxs = sorted([int(k.split('_')[1]) for k in res.keys()])
        for idx in idxs:
            query = self.queries[idx][0].split("/")[0]
            df = transform_query_result(idx, query, res)
            result.append(df)

        return result

    def __batch_gql_queries(self, batched_queries):
        gql_string = "{\n"
        for q in batched_queries:
            gql_string = gql_string + q + "\n"

        gql_string = gql_string + "}"
        return gql_string
