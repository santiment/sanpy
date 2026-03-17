import time
import logging
import san.sanbase_graphql
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Callable, Optional

from san.sanbase_graphql_helper import QUERY_MAPPING
from san.error import SanError

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    """Controls retry behavior for execute_with_retry."""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_factor: float = 2.0
    retry_on_rate_limit: bool = True


@dataclass
class BatchResult:
    """Returned by execute_with_retry. Holds per-query results and errors."""

    results: dict = field(default_factory=dict)
    errors: dict = field(default_factory=dict)

    def to_list(self):
        """Results in original query order, skipping failed queries."""
        return [self.results[i] for i in sorted(self.results)]

    def has_errors(self) -> bool:
        return bool(self.errors)

    def success_rate(self) -> float:
        total = len(self.results) + len(self.errors)
        return len(self.results) / total if total else 1.0


def _is_rate_limit_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "rate limit" in msg or "429" in msg or "too many requests" in msg


def _execute_query(idx, get_type, identifier, kwargs):
    metric, _separator, slug = identifier.partition("/")

    if metric in QUERY_MAPPING or get_type == "get":
        return san.get(identifier, idx=idx, **kwargs)
    elif get_type == "get_many":
        return san.get_many(identifier, idx=idx, **kwargs)
    else:
        raise SanError("Invalid metric!")


def task(request):
    [idx, [get_type, identifier, kwargs]] = request
    return (idx, _execute_query(idx, get_type, identifier, kwargs))


def _task_with_retry(idx: int, query: list, retry_config: RetryConfig):
    get_type, identifier, kwargs = query
    last_exc: Optional[Exception] = None

    for attempt in range(retry_config.max_retries + 1):
        try:
            return _execute_query(idx, get_type, identifier, kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt >= retry_config.max_retries:
                break
            if _is_rate_limit_error(exc) and not retry_config.retry_on_rate_limit:
                break

            delay = min(
                retry_config.base_delay * (retry_config.backoff_factor ** attempt),
                retry_config.max_delay,
            )
            logger.warning(
                "query %d failed (attempt %d/%d): %s. retrying in %.1fs",
                idx,
                attempt + 1,
                retry_config.max_retries,
                exc,
                delay,
            )
            time.sleep(delay)

    raise last_exc


class AsyncBatch:
    def __init__(self):
        self.queries = []

    def get(self, dataset, **kwargs):
        self.queries.append(["get", dataset, kwargs])

    def get_many(self, dataset, **kwargs):
        self.queries.append(["get_many", dataset, kwargs])

    def execute(self, max_workers=10):
        graphql_result = {}

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for idx, response in executor.map(task, enumerate(self.queries)):
                graphql_result[idx] = response

            result = self.__transform_batch_result(graphql_result)
            return result

    def execute_with_retry(
        self,
        max_workers: int = 10,
        retry_config: Optional[RetryConfig] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
        partial_results: bool = False,
    ) -> BatchResult:
        """Execute all queued queries with retry and optional progress tracking.

        Unlike execute(), failed queries are retried with exponential backoff.
        When partial_results=True, per-query failures are collected in
        BatchResult.errors instead of raising immediately, so callers get
        whatever succeeded.

        Args:
            max_workers: thread pool size, same as execute().
            retry_config: retry settings. defaults to RetryConfig().
            on_progress: optional callback(completed, total) after each query.
            partial_results: collect errors per query instead of raising.

        Returns:
            BatchResult with .results and .errors dicts.
        """
        if retry_config is None:
            retry_config = RetryConfig()

        total = len(self.queries)
        completed = 0
        batch_result = BatchResult()

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {
                executor.submit(_task_with_retry, idx, query, retry_config): idx
                for idx, query in enumerate(self.queries)
            }

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                completed += 1

                try:
                    batch_result.results[idx] = future.result()
                except Exception as exc:
                    logger.error("query %d failed after all retries: %s", idx, exc)
                    if partial_results:
                        batch_result.errors[idx] = exc
                    else:
                        raise

                if on_progress is not None:
                    on_progress(completed, total)

        return batch_result

    def __transform_batch_result(self, response_map):
        result = []
        idxs = sorted(idx for idx in response_map.keys())

        for idx in idxs:
            result.append(response_map[idx])

        return result
