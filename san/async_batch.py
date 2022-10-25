import san.sanbase_graphql
import asyncio
from concurrent.futures import ThreadPoolExecutor

from san.sanbase_graphql_helper import QUERY_MAPPING
from san.query import get_gql_query
from san.graphql import execute_gql
from san.transform import transform_timeseries_data_query_result
from san.error import SanError


def task(request):
    [idx, [get_type, identifier, kwargs]] = request
    
    metric, _separator, slug = identifier.partition("/")

    if metric in QUERY_MAPPING:
        response = san.get(identifier, idx=idx, **kwargs)
    elif get_type == 'get':
        response = san.get(identifier, idx=idx, **kwargs)
    elif get_type == 'get_many':
        response = san.get_many(identifier, idx=idx, **kwargs)
    else:
        raise SanError('Invalid metric!')
                
    return (idx, response)

class AsyncBatch:
    def __init__(self):
        self.queries = []

    def get(self, dataset, **kwargs):
        self.queries.append(['get', dataset, kwargs])

    def get_many(self, dataset, **kwargs):
        self.queries.append(['get_many', dataset, kwargs])

    def execute(self, max_workers=10):
        graphql_result = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for (idx, response) in executor.map(task, enumerate(self.queries)):
                graphql_result[idx] = response
            
            result = self.__transform_batch_result(graphql_result)
            return result


    def __transform_batch_result(self, response_map):
        result = []
        print(response_map)
        idxs = sorted(idx for idx in response_map.keys())

        for idx in idxs:
            result.append(response_map[idx])

        return result
