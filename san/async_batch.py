import asyncio

import san
from san.error import SanError
from san.sanbase_graphql_helper import QUERY_MAPPING


async def task(request):
    idx, [get_type, identifier, kwargs] = request

    metric, _separator, slug = identifier.partition("/")

    if metric in QUERY_MAPPING:
        response = await san.get_async(identifier, idx=idx, **kwargs)
    elif get_type == "get":
        response = await san.get_async(identifier, idx=idx, **kwargs)
    elif get_type == "get_many":
        response = await san.get_many_async(identifier, idx=idx, **kwargs)
    else:
        raise SanError("Invalid metric!")

    return (idx, response)


class AsyncBatch:
    def __init__(self):
        self.queries = []

    def get(self, dataset, **kwargs):
        self.queries.append(["get", dataset, kwargs])

    def get_many(self, dataset, **kwargs):
        self.queries.append(["get_many", dataset, kwargs])

    def execute(self, max_workers=10):
        return asyncio.run(self.execute_async(max_workers))

    async def execute_async(self, max_workers=10):
        graphql_result = {}
        sem = asyncio.Semaphore(max_workers)

        async def bounded_task(request):
            async with sem:
                return await task(request)

        tasks = [bounded_task(req) for req in enumerate(self.queries)]
        results = await asyncio.gather(*tasks)

        for idx, response in results:
            graphql_result[idx] = response

        result = self.__transform_batch_result(graphql_result)
        return result

    def __transform_batch_result(self, response_map):
        result = []
        idxs = sorted(response_map.keys())

        for idx in idxs:
            result.append(response_map[idx])

        return result
