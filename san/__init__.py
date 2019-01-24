from .get import get
from .batch import Batch
from .api_config import ApiConfig
import pkg_resources
import requests
import json
from warnings import warn
from multiprocessing import Pool

PROJECT = 'sanpy'

def get_latest():
    url = 'https://pypi.python.org/pypi/%s/json' % (PROJECT)
    try:
      response = requests.get(url).text
      return json.loads(response)['info']['version']
    except requests.exceptions.RequestException as e:
      return pkg_resources.get_distribution(PROJECT).version

def warn_if_outdated():
    project = 'sanpy'
    current_version = pkg_resources.get_distribution(PROJECT).version
    latest_version = get_latest()

    if current_version != latest_version:
      warning = 'The package %s is out of date. Your version is %s, the latest is %s.' % (project, current_version, latest_version)
      warn(warning)
      pass


pool = Pool(processes=1)
pool.apply_async(warn_if_outdated, [])

