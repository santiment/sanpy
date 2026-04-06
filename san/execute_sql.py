from san.client import get_default_client


def execute_sql(**kwargs):
    return get_default_client().execute_sql(**kwargs)
