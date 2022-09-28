import san.sanbase_graphql
import asyncio
from concurrent.futures import ProcessPoolExecutor

from san.sanbase_graphql_helper import QUERY_MAPPING
from san.query import get_gql_query
from san.graphql import execute_gql
from san.transform import transform_query_result
from san.error import SanError


def task(request):
    [idx, [identifier, kwargs]] = request
    
    metric, _separator, slug = identifier.partition("/")

    if metric in QUERY_MAPPING:
        gql_string_query = get_gql_query(idx, identifier, **kwargs)
    elif slug != '':
        gql_string_query = san.sanbase_graphql.get_metric(idx, metric, slug, **kwargs)
    else:
        raise SanError('Invalid metric!')
                
    response = execute_gql("{" + gql_string_query + "}")
    return response

class AsyncBatch:
    def __init__(self):
        self.queries = []

    def get(self, dataset, **kwargs):
        self.queries.append([dataset, kwargs])

    def execute(self, max_workers=10):
        graphql_result = {}

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            for response in executor.map(task, enumerate(self.queries)):
                # response is in the format {'query_0': '<value>'}
                [(key, value)] = list(response.items())
                
                graphql_result[key] = value
            
            result = self.__transform_batch_result(graphql_result)
            return result


    def __transform_batch_result(self, graphql_result):
        result = []
        idxs = sorted([int(k.split('_')[1]) for k in graphql_result.keys()])

        for idx in idxs:
            query = self.queries[idx][0].split("/")[0]
            df = transform_query_result(idx, query, graphql_result)
            result.append(df)
        return result
