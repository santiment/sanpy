from .get import get
from .batch import Batch
from .api_config import ApiConfig
import pkg_resources
import requests
import json
from warnings import warn
import asyncio

PROJECT = 'sanpy'

def get_latest():
    url = 'https://pypi.python.org/pypi/%s/json' % (PROJECT)
    try:
      response = requests.get(url).text
      return json.loads(response)['info']['version']
    except requests.exceptions.RequestException as e:
      return pkg_resources.get_distribution(PROJECT).version

async def warn_if_outdated(): 
    project = 'sanpy'
    current_version = pkg_resources.get_distribution(PROJECT).version
    latest_version = get_latest()

    if current_version != latest_version:
      warning = 'The package %s is out of date. Your version is %s, the latest is %s.' % (project, current_version, latest_version)
      warn(warning)
      pass

# python 3.6 compatible syntax (for 3.7 just asyncio.run(warn_if_outdated()))
loop = asyncio.get_event_loop()
loop.run_until_complete(warn_if_outdated())
loop.close()

