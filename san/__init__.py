import json
from importlib.metadata import PackageNotFoundError, version

import httpx

from .api_config import ApiConfig
from .async_batch import AsyncBatch
from .available_metrics import available_metric_for_slug_since, available_metrics, available_metrics_for_slug
from .batch import Batch
from .cache import clear_cache
from .env_vars import SANPY_APIKEY
from .error import SanAuthError, SanError, SanQueryError, SanRateLimitError, SanValidationError
from .execute_sql import execute_sql
from .get import get, get_async
from .get_many import get_many, get_many_async
from .metadata import metadata
from .metric_complexity import metric_complexity
from .utility import api_calls_made, api_calls_remaining, is_rate_limit_exception, rate_limit_time_left

if SANPY_APIKEY:
    ApiConfig.api_key = SANPY_APIKEY

PROJECT = "sanpy"

try:
    __version__ = version(PROJECT)
except PackageNotFoundError:
    __version__ = "unknown"


def get_latest() -> str:
    url = "https://pypi.python.org/pypi/%s/json" % (PROJECT)
    try:
        response = httpx.get(url).text
        return json.loads(response)["info"]["version"]
    except httpx.RequestError:
        try:
            return version(PROJECT)
        except PackageNotFoundError:
            return "unknown"


__all__ = [
    "__version__",
    "ApiConfig",
    "AsyncBatch",
    "available_metric_for_slug_since",
    "available_metrics",
    "available_metrics_for_slug",
    "Batch",
    "get",
    "get_async",
    "get_many",
    "get_many_async",
    "execute_sql",
    "metadata",
    "metric_complexity",
    "api_calls_made",
    "api_calls_remaining",
    "is_rate_limit_exception",
    "rate_limit_time_left",
    "SanError",
    "SanValidationError",
    "SanRateLimitError",
    "SanAuthError",
    "SanQueryError",
    "clear_cache",
]
