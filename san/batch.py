import san.sanbase_graphql
from san.sanbase_graphql_helper import QUERY_MAPPING
from san.query import get_gql_query
from san.graphql import execute_gql
from san.transform import transform_timeseries_data_query_result
from san.error import SanError


class Batch:
    def __init__(self):
        self.queries = []

    def get(self, dataset, **kwargs):
        self.queries.append([dataset, kwargs])

    def execute(self):
        graphql_string = self.__create_batched_query_string()
        result = execute_gql(graphql_string)
        return self.__transform_batch_result(result)

    def __create_batched_query_string(self):
        batched_queries = []

        for idx, query in enumerate(self.queries):
            [metric, _separator, slug] = query[0].partition('/')
            if metric in QUERY_MAPPING:
                batched_queries.append(
                    get_gql_query(
                        idx, query[0], **query[1]))
            else:
                if slug != '':
                    batched_queries.append(
                        san.sanbase_graphql.get_metric_timeseries_data(
                            idx, metric, slug, **query[1]))
                else:
                    raise SanError('Invalid metric!')
        self.__batch_gql_queries(batched_queries)
        return self.__batch_gql_queries(batched_queries)

    def __transform_batch_result(self, graphql_result):
        result = []

        idxs = sorted([int(k.split('_')[1]) for k in graphql_result.keys()])
        for idx in idxs:
            query = self.queries[idx][0].split("/")[0]
            df = transform_timeseries_data_query_result(idx, query, graphql_result)
            result.append(df)
        return result

    def __batch_gql_queries(self, batched_queries):
        gql_string = "{\n"
        for q in batched_queries:
            gql_string = gql_string + q + "\n"

        gql_string = gql_string + "}"
        return gql_string
