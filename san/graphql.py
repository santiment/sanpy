import requests
from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST
from san.error import SanError


def execute_gql(gql_query_str):
    headers = {}
    if ApiConfig.api_key:
        headers = {'authorization':  "Apikey {}".format(ApiConfig.api_key)}

    response = requests.post(SANBASE_GQL_HOST, json={'query': gql_query_str}, headers=headers)

    if response.status_code == 200:
        return response.json()['data']
    else:
        raise SanError("Error running query. Status code: {}.\n {} \n errors: {}"
            .format(response.status_code, gql_query_str, response.json()['errors']))
