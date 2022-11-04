import json
import os
from warnings import warn

import pkg_resources
import requests

from .api_config import ApiConfig
from .async_batch import AsyncBatch
from .available_metrics import (available_metric_for_slug_since,
                                available_metrics, available_metrics_for_slug)
from .batch import Batch
from .env_vars import SANPY_APIKEY
from .get import get
from .get_many import get_many
from .metadata import metadata
from .metric_complexity import metric_complexity
from .utility import (api_calls_made, api_calls_remaining,
                      is_rate_limit_exception, rate_limit_time_left)

if SANPY_APIKEY:
    ApiConfig.api_key = SANPY_APIKEY

PROJECT = 'sanpy'

def get_latest():
    url = 'https://pypi.python.org/pypi/%s/json' % (PROJECT)
    try:
        response = requests.get(url).text
        return json.loads(response)['info']['version']
    except requests.exceptions.RequestException as e:
        return pkg_resources.get_distribution(PROJECT).version
