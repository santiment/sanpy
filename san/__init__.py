from .get import get
from .batch import Batch
from .api_config import ApiConfig
import pkg_resources
import requests
import json
from warnings import warn

def get_latest(project):
    url = 'https://pypi.python.org/pypi/%s/json' % (project)
    try:
      response = requests.get(url).text
      return json.loads(response)['info']['version']
    except requests.exceptions.RequestException as e:
      return pkg_resources.require(project)[0].version

project = 'sanpy'
current_version = pkg_resources.require(project)[0].version
latest = get_latest(project)

if current_version != latest:
    warning = 'The package %s is out of date. Your version is %s, the latest is %s.' % (project, current_version, latest)
    warn(warning)
