from san.client import get_default_client


def get_many(dataset, **kwargs):
    return get_default_client().get_many(dataset, **kwargs)
