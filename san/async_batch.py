import asyncio
from typing import Any

import pandas as pd

import san
from san.error import SanValidationError
from san.sanbase_graphql_helper import QUERY_MAPPING


async def task(request: tuple[int, list[Any]]) -> tuple[int, pd.DataFrame]:
    idx, [get_type, identifier, kwargs] = request

    metric, _separator, slug = identifier.partition("/")

    if metric in QUERY_MAPPING:
        response = await san.get_async(identifier, idx=idx, **kwargs)
    elif get_type == "get":
        response = await san.get_async(identifier, idx=idx, **kwargs)
    elif get_type == "get_many":
        response = await san.get_many_async(identifier, idx=idx, **kwargs)
    else:
        raise SanValidationError("Invalid metric!")

    return (idx, response)


class AsyncBatch:
    """Execute multiple queries concurrently using asyncio.

    Each query is sent as a separate HTTP request and executed
    concurrently, controlled by the ``max_workers`` parameter.
    Supports both :meth:`get` and :meth:`get_many` queries.

    Each query still counts as a separate API call for rate-limiting.
    """

    def __init__(self) -> None:
        self.queries: list[list[Any]] = []

    def get(self, dataset: str, **kwargs: Any) -> None:
        self.queries.append(["get", dataset, kwargs])

    def get_many(self, dataset: str, **kwargs: Any) -> None:
        self.queries.append(["get_many", dataset, kwargs])

    def execute(self, max_workers: int = 10) -> list[pd.DataFrame]:
        return asyncio.run(self.execute_async(max_workers))

    async def execute_async(self, max_workers: int = 10) -> list[pd.DataFrame]:
        graphql_result: dict[int, pd.DataFrame] = {}
        sem = asyncio.Semaphore(max_workers)

        async def bounded_task(request: tuple[int, list[Any]]) -> tuple[int, pd.DataFrame]:
            async with sem:
                return await task(request)

        tasks = [bounded_task(req) for req in enumerate(self.queries)]
        results = await asyncio.gather(*tasks)

        for idx, response in results:
            graphql_result[idx] = response

        result = self.__transform_batch_result(graphql_result)
        return result

    def __transform_batch_result(self, response_map: dict[int, pd.DataFrame]) -> list[pd.DataFrame]:
        result = []
        idxs = sorted(response_map.keys())

        for idx in idxs:
            result.append(response_map[idx])

        return result
