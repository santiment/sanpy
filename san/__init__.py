from .get import get
from .metadata import metadata
from .available_metrics import available_metrics
from .batch import Batch
from .api_config import ApiConfig
import pkg_resources
import httpx
import json
from warnings import warn

PROJECT = 'sanpy'


def get_latest():
    url = 'https://pypi.python.org/pypi/%s/json' % (PROJECT)
    try:
        response = httpx.get(url).text
        return json.loads(response)['info']['version']
    except httpx.exceptions.HTTPError as e:
        return pkg_resources.get_distribution(PROJECT).version


def warn_if_outdated():
    current_version = pkg_resources.get_distribution(PROJECT).version
    latest_version = get_latest()

    if current_version != latest_version:
        warning = 'The package %s is out of date. Your version is %s, the latest is %s.' % (
            PROJECT, current_version, latest_version)
        warn(warning)
        pass


warn_if_outdated()
