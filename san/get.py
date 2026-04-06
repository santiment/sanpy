from san.client import get_default_client


def get(dataset, **kwargs):
    return get_default_client().get(dataset, **kwargs)
