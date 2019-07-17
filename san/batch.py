from san.query import get_gql_query
from san.graphql import execute_gql
from san.transform import transform_query_result


class Batch:

    def __init__(self):
        self.queries = []

    def get(self, dataset, **kwargs):
        self.queries.append([dataset, kwargs])

    def execute(self):
        result = []
        batched_queries = []

        for idx, q in enumerate(self.queries):
            batched_queries.append(get_gql_query(idx, q[0], **q[1]))

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
