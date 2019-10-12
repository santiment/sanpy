from .get import get
from .metadata import metadata
from .available_metrics import available_metrics
from .batch import Batch
from .api_config import ApiConfig
import asyncio
import pkg_resources
import httpx
import json
from warnings import warn

PROJECT = 'sanpy'


async def get_latest():
    url = 'https://pypi.python.org/pypi/%s/json' % (PROJECT)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
        return json.loads(response.text)['info']['version']
    except httpx.exceptions.HTTPError as e:
        return pkg_resources.get_distribution(PROJECT).version


async def warn_if_outdated():
    current_version = pkg_resources.get_distribution(PROJECT).version
    latest_version = await get_latest()

    if current_version != latest_version:
        warning = 'The package %s is out of date. Your version is %s, the latest is %s.' % (
            PROJECT, current_version, latest_version)
        warn(warning)
        pass

try:
    asyncio.run(warn_if_outdated())
except RuntimeError:
    asyncio.create_task(warn_if_outdated())
