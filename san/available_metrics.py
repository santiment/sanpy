from san.client import get_default_client


def available_metrics():
    return get_default_client().available_metrics()


def available_metrics_for_slug(slug):
    return get_default_client().available_metrics_for_slug(slug)


def available_metric_for_slug_since(metric, slug):
    return get_default_client().available_metric_for_slug_since(metric, slug)
