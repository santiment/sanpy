from san.client import get_default_client


def metric_complexity(metric, from_date, to_date, interval):
    return get_default_client().metric_complexity(metric, from_date, to_date, interval)
