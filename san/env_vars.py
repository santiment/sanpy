import os

SANBASE_GQL_HOST = os.environ.get(
    'SANBASE_GQL_HOST',
    "https://api.santiment.net/graphql")

SANPY_APIKEY = os.environ.get(
    'SANPY_APIKEY',
    None)
