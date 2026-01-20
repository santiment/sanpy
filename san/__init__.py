import json

import requests
from importlib.metadata import version, PackageNotFoundError

from .api_config import ApiConfig
from .async_batch import AsyncBatch
from .available_metrics import available_metric_for_slug_since, available_metrics, available_metrics_for_slug
from .batch import Batch
from .env_vars import SANPY_APIKEY
from .get import get
from .get_many import get_many
from .execute_sql import execute_sql
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


def get_latest():
    url = "https://pypi.python.org/pypi/%s/json" % (PROJECT)
    try:
        response = requests.get(url).text
        return json.loads(response)["info"]["version"]
    except requests.exceptions.RequestException:
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
    "get_many",
    "execute_sql",
    "metadata",
    "metric_complexity",
    "api_calls_made",
    "api_calls_remaining",
    "is_rate_limit_exception",
    "rate_limit_time_left",
]
