from .client import get_default_client


def metadata(metric, arr):
    return get_default_client().metadata(metric, arr)
